"""Provide the setuptools command bdist_rpm2."""

from setuptools.command.bdist_rpm import bdist_rpm


class bdist_rpm2(bdist_rpm):
    """Add two extra user options to the setuptools bdist_rpm command:
    - name-prefix: specify a custom prefix name for the RPM build
    - run-test: add 'python setup.py test' to the %check section
    """

    # Description
    description = "modified version of bdist_rpm"

    # Copy user options
    user_options = list(bdist_rpm.user_options)

    # Add name-prefix option
    user_options.append((
        'name-prefix=', None,
        "Specify a custom prefix name for the RPM build"))

    # Add run-test option
    user_options.append((
        'run-test', None,
        "Add 'python setup.py test' to the %check section"))

    def initialize_options(self):
        self.name_prefix = ''
        self.run_test = 0
        bdist_rpm.initialize_options(self)

    def finalize_package_data(self):
        self.ensure_string('name_prefix')
        self.name_prefix = self.name_prefix.rstrip('-')
        bdist_rpm.finalize_package_data(self)

    def run(self):
        metadata = self.distribution.metadata
        save_name = metadata.name
        # Add prefix to package back
        print(self.name_prefix)
        if self.name_prefix:
            metadata.name = '-'.join((self.name_prefix, save_name))
        # Run bdist_rpm
        try:
            bdist_rpm.run(self)
        # Revert the change
        finally:
            metadata.name = save_name

    def _make_spec_file(self):
        spec_file = bdist_rpm._make_spec_file(self)
        # Add tests to the spec file
        if self.run_test:
            test_call = "%s setup.py test" % self.python
            spec_file.extend(['', '%check', test_call])
        return spec_file
