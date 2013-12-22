ROOTDIR = $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHONHOME = ${ROOTDIR}/venv/
LOCAL_SETTINGS = ${ROOTDIR}/famille/core/local_settings.py
LOCAL_SETTINGS_TPL = ${LOCAL_SETTINGS}.tpl

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
	$(call cp-settings, ${LOCAL_SETTINGS_TPL}, ${LOCAL_SETTINGS})

test:
	./manage.py test
