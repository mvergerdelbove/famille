ROOTDIR = $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHONHOME = ${ROOTDIR}/venv/
LOCAL_ENV = ${ROOTDIR}/.env
LOCAL_ENV_TPL = ${LOCAL_ENV}.tpl

.SILENT: install venv settings test dependencies

# function to copy settings templates
cp-settings = ([ ! -f $(1) ]) || ([ -f $(2) ] && echo "File already exists.") || (cp -n $(1) $(2))

install: venv settings dependencies

dependencies:
	npm install
	${PYTHONHOME}bin/pip install -r requirements.txt

venv:
	echo "Creating virtualenv..."
	(test -d ${PYTHONHOME} || virtualenv ${PYTHONHOME})

settings:
	echo 'Copying settings...'
	$(call cp-settings, ${LOCAL_ENV_TPL}, ${LOCAL_ENV})

test:
	set -a && . ${LOCAL_ENV} && set +a && ${PYTHONHOME}/bin/python manage.py test --noinput

schemamigration:
	foreman run ./manage.py schemamigration famille --auto

migration:
	foreman run ./manage.py migrate famille
