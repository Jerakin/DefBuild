clean:
	rm -rf *.egg-info
	rm -rf dist

build:
	python setup.py bdist_wheel

install:
	pip install ./dist/defbuild-$(shell cat "./defbuild/__init__.py" | grep -Eo "[0-9\.ab]{5,}")-py3-none-any.whl

publish:
	python setup.py clean --all bdist_wheel
	twine upload ./dist/defbuild-$(shell cat "./defbuild/__init__.py" | grep -Eo "[0-9\.ab]{5,}")-py3-none-any.whl
	git tag v$(shell cat "./defbuild/__init__.py" | grep -Eo "[0-9\.ab]{5,}")

.PHONY: clean build install publish

