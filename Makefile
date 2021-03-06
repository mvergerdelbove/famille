ROOTDIR = $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHONHOME = ${ROOTDIR}/venv/
LOCAL_ENV = ${ROOTDIR}/.env
LOCAL_ENV_TPL = ${LOCAL_ENV}.tpl
ACTIVATE_VENV = . ${PYTHONHOME}bin/activate
PYTHON_RUNNER = ${ACTIVATE_VENV} &&

.SILENT: install venv settings test dependencies

# function to copy settings templates
cp-settings = ([ ! -f $(1) ]) || ([ -f $(2) ] && echo "File already exists.") || (cp -n $(1) $(2))

install: venv settings dependencies

install_test: venv settings pydependencies

up: dependencies migrate

up_dev: up fixtures

dependencies: pydependencies jsdependencies

pydependencies:
	${PYTHON_RUNNER} pip install -q -r requirements.txt

jsdependencies:
	npm install --loglevel error

venv:
	echo "Creating virtualenv..."
	(test -d ${PYTHONHOME} || virtualenv ${PYTHONHOME})

settings:
	echo 'Copying settings...'
	$(call cp-settings, ${LOCAL_ENV_TPL}, ${LOCAL_ENV})

test:
	set -a && . ${LOCAL_ENV} && set +a && ${PYTHONHOME}/bin/python manage.py test --noinput

schemamigration:
	${PYTHON_RUNNER} foreman run ./manage.py schemamigration famille --auto

migrate:
	${PYTHON_RUNNER} foreman run ./manage.py migrate famille || ./manage.py migrate famille

fixtures:
	${PYTHON_RUNNER} foreman run ./manage.py loaddata prestataires.json keygroup.json
