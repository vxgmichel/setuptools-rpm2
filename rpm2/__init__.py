"""Provide the setuptools command bdist_rpm2.
It adds two extra user options to the bdist_rpm setuptools command:
- name-prefix: specify a custom prefix name for the RPM build
- run-test: add 'python setup.py test' to the %check section
"""
