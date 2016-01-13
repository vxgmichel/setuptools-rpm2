rpm2
====

Provide a modified version setuptools command `bdist_rpm` called `bdist_rpm2`.

It adds two extra user options to the `bdist_rpm`:
- --name-prefix: specify a custom prefix name for the RPM build
- --run-test: add 'python setup.py test' to the %check section
- --spec-and-source: generate the spec file and the source distribution


Requirements
------------

- setuptools


Usage
-----

For a python project called 'mypackage':

```bash
$ python setup.py bdist_rpm2 [...] --name-prefix=python --run-test
# Build a rpm package called 'python-mypackage' and run the unit tests
```

Contact
-------

Vincent Michel: vxgmichel@gmail.com

