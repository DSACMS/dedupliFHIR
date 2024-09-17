.PHONY:
install:
	poetry install

test:
	cd cli; poetry run python -m pytest deduplifhirLib/tests/

dist:
	./set-up-python-env.sh; cd frontend; electron-builder --publish never -c.win.verifyUpdateCodeSignature=false
