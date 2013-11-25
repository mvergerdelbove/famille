ROOTDIR = $(realpath $(dir $(lastword $(MAKEFILE_LIST))))
PYTHONHOME = ${ROOTDIR}/venv/

install: venv
	${PYTHONHOME}bin/pip install -r requirements.txt

venv:
	echo "Creating virtualenv..."
	(test -d ${PYTHONHOME} || virtualenv ${PYTHONHOME})