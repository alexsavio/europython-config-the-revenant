### Configuration

# Place the domains into the domains.txt file. The first domain will
# be used as main domain of the certificate. The others as SAN domains.

# Parameters
export LE_HOME := $(shell pwd)
export LE_DOMAINS = /etc/letsencrypt/domains.txt
export LE_ACCOUNT_EMAIL = webmaster@europython.eu
export LE_WORKING_DIR = $(LE_HOME)/script
export ACCOUNT_CONF_PATH = $(LE_HOME)/etc/le-account.conf

# Parse domains for the certificate
ALL_DOMAINS := $(shell cat $(LE_DOMAINS) | sed -e '/^\#.*$$/d' -e '/^ *$$/d')
MAIN_DOMAIN := $(shell echo $(ALL_DOMAINS) | tr ' ' '\n' | head -1)
SAM_DOMAINS := $(shell echo $(ALL_DOMAINS) | tr ' ' '\n' | tail -n +2)
D_ALL_DOMAINS := $(shell echo $(ALL_DOMAINS) | tr ' ' '\n' | sed -e 's/^/-d /g')

# Backup dir to use for this run
BACKUP_DIR = `date +%Y%m%d-%H%M%S`

###

all:
	@echo "See Makefile for details."

### Setup

clean:
	rm -rf certs/* acme-challenge/*

distclean:	clean
	rm -rf installation script private etc backups logs \
		acme-challenge/.well-known

dirs:
	mkdir -p installation script certs private etc backups logs
	chmod 750 certs
	chmod 700 private backups
	chmod 750 script
	mkdir -p acme-challenge/.well-known; \
	cd acme-challenge/.well-known; \
	ln -sf .. acme-challenge

installation/acme.sh:
	curl -L https://github.com/Neilpang/acme.sh/raw/master/acme.sh > \
		installation/acme.sh
	chmod +x installation/acme.sh
	touch $@

script/acme.sh:	dirs installation/acme.sh
	cd installation; \
	./acme.sh --install \
		--home $(LE_WORKING_DIR) \
		--certhome  $(LE_HOME)/certs \
		--accountemail $(LE_ACCOUNT_EMAIL) \
		--accountkey  $(LE_HOME)/private/le-account.key \
		--accountconf $(LE_HOME)/etc/le-account.conf \
		--nocron \
		--log $(LE_HOME)/logs/acme.log
	touch $@

install:	script/acme.sh

### Account creation

private/le-account.key:
	script/acme.sh --createAccountKey --accountkeylength 4096
	script/acme.sh --registeraccount

create-account:	private/le-account.key

### Backups

backup:
	mkdir -p backups/$(BACKUP_DIR)/
	cp -a certs backups/$(BACKUP_DIR)/

### Certificate creation

test-issue-certificate:	backup
	script/acme.sh --test --issue --force --log --debug \
		--keylength 4096 -w acme-challenge/ \
		$(D_ALL_DOMAINS)
	touch certs/THESE_ARE_TEST_CERTS

issue-certificate:	backup
	script/acme.sh --issue --keylength 4096 -w acme-challenge/ \
		$(D_ALL_DOMAINS)
	rm -f certs/THESE_ARE_TEST_CERTS

reissue-certificate:	backup
	script/acme.sh --issue --force --keylength 4096 -w acme-challenge/ \
		$(D_ALL_DOMAINS)
	rm -f certs/THESE_ARE_TEST_CERTS

check-certificate:
	openssl x509 -text -in certs/$(MAIN_DOMAIN)/$(MAIN_DOMAIN).cer

cron-update:
	script/acme.sh --cron >> $(LE_HOME)/logs/update.log

### DH parameter generation

dh-params:
	openssl dhparam -out $(LE_HOME)/certs/dhparam.pem 2048

### Debugging

print-config:
	@echo "LE_WORKING_DIR: $(LE_WORKING_DIR)"
	@echo "ACCOUNT_CONF_PATH: $(ACCOUNT_CONF_PATH)"
	@echo ""
	@echo "Main domain: $(MAIN_DOMAIN)"
	@echo ""
	@echo "SAM domains: $(SAM_DOMAINS)"
	@echo ""
	@echo "-d all domains: $(D_ALL_DOMAINS)"
	@echo "Environment:"
	@env

