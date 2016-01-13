rpm2
====

Provide a setuptools command called bdist_rpm2.

It adds two extra user options to the `bdist_rpm` setuptools command:
- name-prefix: specify a custom prefix name for the RPM build
- run-test: add 'python setup.py test' to the %check section


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

