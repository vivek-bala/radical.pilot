
.PHONY: clean

clean:
	-rm -rf build/ src/sinon.egg-info/ temp/ MANIFEST dist/ src/sinon/VERSION pylint.out *.egg
	find . -name \*.pyc -exec rm -f {} \;

-include Makefile.andre
