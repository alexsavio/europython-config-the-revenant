#!/usr/bin/env python2

"""
TODO(artcz) 2018-04-12:
    This is a placeholder for a real update/deploy script (probalby based in
ansible)

"""

from __future__ import print_function

from datetime import datetime
from subprocess import Popen, PIPE
import logging
import sys


# May need to add older epcons if we have some security updates.
AVAILABLE_EPCONS = ['epstage', 'ep2018']
# actual names of containers are not the same in docker and docker-compose.
# we need both to run `docker exec` and `docker-compose ... restart`
CONTAINER_NAMES = {
    'epstage': 'webarch_epstage_1',
    'ep2018':  'webarch_ep2018_1',
}
WORKDIR = "/home/webarch/"
DRY_RUN = False
LOGFILE_PATH = "/root/deploy_epcon.log"
STAGING = "epstage"
DEFAULT_STAGING_BRANCH = "ep2018"

logger = logging.getLogger('deploy_epcon')
logger.setLevel(logging.DEBUG)
logfile_formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s'
)
console_formatter = logging.Formatter('%(levelname)s - %(message)s')

console = logging.StreamHandler()
logfile = logging.FileHandler(filename=LOGFILE_PATH)

for handler in console, logfile:
    handler.setLevel(logging.DEBUG)

console.setFormatter(console_formatter)
logger.addHandler(console)

logfile.setFormatter(logfile_formatter)
logger.addHandler(logfile)


def sh(cmd, skip_log=False):
    """
    Helper to run a shell command using subprocess.call, while adding some
    debug info
    """
    if DRY_RUN:
        logger.info("DRY RUN >> [%s] $ %s", WORKDIR, cmd)
    else:
        logger.info(">> [%s] $ %s", WORKDIR, cmd)

    if not DRY_RUN:
        p = Popen(cmd.split(), cwd=WORKDIR, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if stdout:
            to_log = stdout.rstrip()
            if skip_log:
                logger.info("<skipping stdout log... %d chars>", len(to_log))
            else:
                logger.info(to_log)
        if stderr and not skip_log:
            to_log = stderr.rstrip()
            if skip_log:
                logger.info("<skipping stdout log... %d chars>", len(to_log))
            else:
                logger.error(to_log)

    return stdout.rstrip(), stderr.rstrip()


def title(s):
    if DRY_RUN:
        logger.info('DRY_RUN ' + '-'*len(s))
        logger.info('DRY_RUN ' + s)
        logger.info('DRY_RUN ' + '='*len(s))
    else:
        logger.info('-'*len(s))
        logger.info(s)
        logger.info('='*len(s))


def backup_db(container_name):
    title("Making db backup of %s" % container_name)
    db_path = WORKDIR + "volumes/webarch_%s_data_site/_data/p3.db" % container_name
    backup_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = WORKDIR + 'volumes/webarch_%s_data_site/_data/p3_%s.db' % (container_name, backup_id)
    sh('cp %(db_path)s %(backup_path)s' % {'db_path':db_path, 'backup_path':backup_path})


def copy_latest_production_db_to_epstage():
    title("Copying production db to epstage")
    source = WORKDIR + "volumes/webarch_ep2018_data_site/_data/p3.db"
    destination = WORKDIR + "volumes/webarch_epstage_data_site/_data/p3.db"
    sh("cp %(source)s %(destination)s" % {
        'source': source,
        'destination': destination
    })



def check_if_requirements_changed(stdout, stderr):
    REQUIREMENTS_FILE_NAME = "requirements"
    if REQUIREMENTS_FILE_NAME in (''.join(stdout) + ''.join(stderr)):
        return True
    return False


def update_container(container_name, commit_hash=None):
    def docker_exec(cmd, skip_log=False):
        return sh(
            "docker exec %s %s" % (CONTAINER_NAMES[container_name], cmd),
            skip_log=skip_log
        )

    def run_pip_install_requirements():
        docker_exec("pip install -r requirements.txt")

    def do_smart_checkout(target):
        """
        Does smarter git checkout that logs both source and target, and then
        diffstat between the two
        """
        source, _ = docker_exec('git rev-parse HEAD')
        logger.info("SMART CHECKOUT: Jumping from %s to %s", source[:7], target)
        docker_exec("git checkout %s" % target)
        diffstat = docker_exec("git diff --stat %s" % source)
        if check_if_requirements_changed(*diffstat):
            logger.info("REQUIREMENTS CHANGED RUNNING PIP INSTALL")
            logger.info("(because it's staging we run pip inside container)")
            run_pip_install_requirements()
        return diffstat


    backup_db(container_name)
    if container_name == STAGING:
        copy_latest_production_db_to_epstage()

    title("UPDATING CONTAINER %s with %s" % (container_name, commit_hash))
    if container_name == STAGING:
        commit_hash = commit_hash or DEFAULT_STAGING_BRANCH
        # this if could probably be replaced with just 'fetch&checkout' but for
        # that to work we need to get rid of a local copy of the staging
        # branch. for now - applying workaround
        if commit_hash != DEFAULT_STAGING_BRANCH:
            docker_exec("git fetch")
            do_smart_checkout(commit_hash)
        else:
            do_smart_checkout(DEFAULT_STAGING_BRANCH)
            docker_exec("git pull")

        docker_exec("./manage.py migrate --noinput")
        docker_exec("./manage.py collectstatic --clear --noinput", skip_log=True)
        sh("docker-compose restart %s" % container_name)

    else:
        stdin_and_err_incl_diffstat = docker_exec("git pull")
        if check_if_requirements_changed(*stdin_and_err_incl_diffstat):
            logger.warning("REQUIREMENTS CHANGED PLEASE REBUILD THE CONTAINER")
            logger.warning("REQUIREMENTS CHANGED PLEASE REBUILD THE CONTAINER")
            logger.warning("REQUIREMENTS CHANGED PLEASE REBUILD THE CONTAINER")
        docker_exec("./manage.py migrate --noinput")
        docker_exec("./manage.py collectstatic --noinput")
        sh("docker-compose restart %s" % container_name)


def arguments_are_valid():
    if len(sys.argv) <= 1:
        print("Not enough arguments")
        return False
    elif len(sys.argv) > 3:
        print("too many arguments; pass just a name of the container")
        return False
    elif sys.argv[1] == STAGING and len(sys.argv) == 2:
        # easier to write a positive check here and return True
        # it's for optional case where we want to do git fetch and checkout
        # instead of git pull (useful if we want to deploy different
        # commit/branch)
        return True
    elif sys.argv[1] not in AVAILABLE_EPCONS:
        print("%s not in %s" % (sys.argv[1], AVAILABLE_EPCONS))
        return False

    return True


if __name__ == "__main__":
    if arguments_are_valid():
        update_container(*sys.argv[1:])

    logger.info("-------------- Finished deployment ---------------")
