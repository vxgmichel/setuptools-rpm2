"""Provide the setuptools command bdist_rpm2."""

import os
from setuptools.command.bdist_rpm import bdist_rpm
from setuptools.command.sdist import sdist
from distutils.errors import DistutilsOptionError


class bdist_rpm2(bdist_rpm):
    """Add two extra user options to the setuptools bdist_rpm command:
     --name-prefix: specify a custom prefix name for the RPM build
     --run-test: add 'python setup.py test' to the %check section
     --spec-and-source: generate the spec file and the source distribution
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

    # Add run-test option
    user_options.append((
        'spec-and-source', None,
        "Generate only the spec file and the source distribution"))

    def initialize_options(self):
        self.name_prefix = ''
        self.run_test = 0
        self.spec_and_source = 0
        bdist_rpm.initialize_options(self)

    def finalize_package_data(self):
        # Name prefix argument
        self.ensure_string('name_prefix')
        self.name_prefix = self.name_prefix.rstrip('-')
        # Spec and source argument
        if self.spec_and_source and self.spec_only:
            raise DistutilsOptionError(
                "cannot supply both '--spec-only' and '--spec-and-source'")
        if self.spec_and_source:
            self.spec_only = 1
        bdist_rpm.finalize_package_data(self)

    def run(self):
        # Prepare run
        metadata = self.distribution.metadata
        metadata.rpm_name_prefix = self.name_prefix
        save_sdist = self.distribution.get_command_class('sdist')
        self.distribution.cmdclass['sdist'] = sdist2
        # Run bdist_rpm
        try:
            bdist_rpm.run(self)
            if self.spec_and_source:
                self._make_source_dist()
        # Revert the change
        finally:
            self.distribution.cmdclass['sdict'] = save_sdist
            del metadata.rpm_name_prefix

    def execute(self, func, args, msg):
        try:
            if self.name_prefix and args[0].endswith('.spec'):
                base, name = os.path.split(args[0])
                new_name = '-'.join((self.name_prefix, name))
                base_name = os.path.join(base, new_name)
                args = (base_name,) + args[1:]
        except (AttributeError, TypeError, IndexError):
            pass
        return bdist_rpm.execute(self, func, args, msg)

    def _make_source_dist(self):
        saved_dist_files = self.distribution.dist_files[:]
        try:
            sdist = self.reinitialize_command('sdist')
            sdist.dist_dir = self.dist_dir
            sdist.formats = ['bztar'] if self.use_bzip2 else ['gztar']
            self.run_command('sdist')
        finally:
            self.distribution.dist_files = saved_dist_files

    def _make_spec_file(self):
        spec_file = bdist_rpm._make_spec_file(self)
        # Add tests to the spec file
        if self.run_test:
            test_call = "%s setup.py test" % self.python
            spec_file.extend(['', '%check', test_call])
        # Add name prefix
        if self.name_prefix:
            name = self.distribution.get_name()
            name = '-'.join((self.name_prefix, name))
            spec_file[0] = "%define name " + name
        return spec_file


class sdist2(sdist):

    def make_release_tree(self, base_dir, files):
        metadata = self.distribution.metadata
        try:
            if metadata.rpm_name_prefix:
                base_dir = '-'.join((metadata.rpm_name_prefix, base_dir))
        except AttributeError:
            pass
        return sdist.make_release_tree(self, base_dir, files)

    def make_archive(self, base_name, *args, **kwargs):
        metadata = self.distribution.metadata
        try:
            if metadata.rpm_name_prefix:
                base, name = os.path.split(base_name)
                new_name = '-'.join((metadata.rpm_name_prefix, name))
                base_name = os.path.join(base, new_name)
                if 'base_dir' in kwargs:
                    kwargs['base_dir'] = new_name
        except AttributeError:
            pass
        return sdist.make_archive(self, base_name, *args, **kwargs)
