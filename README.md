rpm2
====

Provide a modified version setuptools command `bdist_rpm` called `bdist_rpm2`.

It adds two extra user options to the `bdist_rpm`:
- --dist-name: specify a different distribution name
- --run-test: add 'python setup.py test' to the %check section

It also uses a modified version of the command `sdist` called `sdist2`, that
adds a similar `--dist-name` user option.

Requirements
------------

- setuptools


Usage
-----

For a python project called 'mypackage':

```bash
$ python setup.py bdist_rpm2 [...] --dist-name=python-mypackage --run-test
# Build a rpm package called 'python-mypackage' and run the unit tests
```

Contact
-------

Vincent Michel: vxgmichel@gmail.com
