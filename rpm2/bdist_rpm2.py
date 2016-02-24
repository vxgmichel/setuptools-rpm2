"""Provide the setuptools command bdist_rpm2."""

import os
import string

from setuptools.command.bdist_rpm import bdist_rpm


from distutils.debug import DEBUG
from distutils.file_util import write_file
from distutils.sysconfig import get_python_version
from distutils.errors import DistutilsFileError, DistutilsExecError
from distutils import log


class bdist_rpm2(bdist_rpm):
    """Add two extra user options to the setuptools bdist_rpm command:
     --dist-name: specify a different distribution name
     --add-test: add 'python setup.py test' to the %check section
    """

    # Description
    description = "modified version of bdist_rpm"

    # Copy user options
    user_options = list(bdist_rpm.user_options)

    # Add name-prefix option
    user_options.append((
        'dist-name=', None,
        "Specify a different distribution name"))

    # Add run-test option
    user_options.append((
        'add-test', None,
        "Add 'python setup.py test' to the %check section"))

    def initialize_options(self):
        self.dist_name = ''
        self.add_test = 0
        bdist_rpm.initialize_options(self)

    def finalize_package_data(self):
        self.ensure_string('dist_name')
        self.dist_name = self.dist_name.strip()
        # Patch EncodingError in bdist_rpm
        metadata = self.distribution.metadata
        metadata.author_email = metadata._encode_field(metadata.author_email)
        # Call parent
        bdist_rpm.finalize_package_data(self)

    def get_distribution_name(self):
        if self.dist_name:
            return self.dist_name
        return self.distribution.get_name()

    def _make_spec_file(self):
        spec_file = bdist_rpm._make_spec_file(self)
        # Add tests to the spec file
        if self.add_test:
            test_call = "%s setup.py test" % self.python
            spec_file.extend(['', '%check', test_call])
        # Change dist name
        if self.dist_name:
            spec_file[0] = "%define name " + self.dist_name
        return spec_file

    # The rest of the file is shamelessly copied from
    # distutils/command/bdist_rpm.py. The only modifications are:
    # - the declaration of the `spec_path` variable, where the distribution
    # name is `self.get_distribution_name()`
    # - the use of `sdist2` instead of `sdist`

    def run(self):

        # ensure distro name is up-to-date
        self.run_command('egg_info')

        if DEBUG:
            print "before _get_package_data():"
            print "vendor =", self.vendor
            print "packager =", self.packager
            print "doc_files =", self.doc_files
            print "changelog =", self.changelog

        # make directories
        if self.spec_only:
            spec_dir = self.dist_dir
            self.mkpath(spec_dir)
        else:
            rpm_dir = {}
            for d in ('SOURCES', 'SPECS', 'BUILD', 'RPMS', 'SRPMS'):
                rpm_dir[d] = os.path.join(self.rpm_base, d)
                self.mkpath(rpm_dir[d])
            spec_dir = rpm_dir['SPECS']

        # Spec file goes into 'dist_dir' if '--spec-only specified',
        # build/rpm.<plat> otherwise.

        spec_path = os.path.join(
            spec_dir,
            "%s.spec" % self.get_distribution_name())
        self.execute(write_file,
                     (spec_path,
                      self._make_spec_file()),
                     "writing '%s'" % spec_path)

        if self.spec_only:  # stop if requested
            return

        # Make a source distribution and copy to SOURCES directory with
        # optional icon.
        saved_dist_files = self.distribution.dist_files[:]
        sdist = self.reinitialize_command('sdist2')
        sdist.dist_name = self.dist_name
        if self.use_bzip2:
            sdist.formats = ['bztar']
        else:
            sdist.formats = ['gztar']
        self.run_command('sdist2')
        self.distribution.dist_files = saved_dist_files

        source = sdist.get_archive_files()[0]
        source_dir = rpm_dir['SOURCES']
        self.copy_file(source, source_dir)

        if self.icon:
            if os.path.exists(self.icon):
                self.copy_file(self.icon, source_dir)
            else:
                error = "icon file '%s' does not exist" % self.icon
                raise DistutilsFileError(error)

        # build package
        log.info("building RPMs")
        rpm_cmd = ['rpm']
        if os.path.exists('/usr/bin/rpmbuild') or \
           os.path.exists('/bin/rpmbuild'):
            rpm_cmd = ['rpmbuild']

        if self.source_only:  # what kind of RPMs?
            rpm_cmd.append('-bs')
        elif self.binary_only:
            rpm_cmd.append('-bb')
        else:
            rpm_cmd.append('-ba')
        if self.rpm3_mode:
            rpm_cmd.extend(['--define',
                            '_topdir %s' % os.path.abspath(self.rpm_base)])
        if not self.keep_temp:
            rpm_cmd.append('--clean')

        if hasattr(self, 'quiet') and self.quiet:
            rpm_cmd.append('--quiet')

        rpm_cmd.append(spec_path)
        # Determine the binary rpm names that should be built out of this spec
        # file
        # Note that some of these may not be really built (if the file
        # list is empty)
        nvr_string = "%{name}-%{version}-%{release}"
        src_rpm = nvr_string + ".src.rpm"
        non_src_rpm = "%{arch}/" + nvr_string + ".%{arch}.rpm"
        q_cmd = r"rpm -q --qf '%s %s\n' --specfile '%s'" % (
            src_rpm, non_src_rpm, spec_path)

        out = os.popen(q_cmd)
        try:
            binary_rpms = []
            source_rpm = None
            while 1:
                line = out.readline()
                if not line:
                    break
                l = string.split(string.strip(line))
                assert(len(l) == 2)
                binary_rpms.append(l[1])
                # The source rpm is named after the first entry in the specfile
                if source_rpm is None:
                    source_rpm = l[0]

            status = out.close()
            if status:
                raise DistutilsExecError("Failed to execute: %s" % repr(q_cmd))

        finally:
            out.close()

        self.spawn(rpm_cmd)

        if not self.dry_run:
            if self.distribution.has_ext_modules():
                pyversion = get_python_version()
            else:
                pyversion = 'any'

            if not self.binary_only:
                srpm = os.path.join(rpm_dir['SRPMS'], source_rpm)
                assert(os.path.exists(srpm))
                self.move_file(srpm, self.dist_dir)
                filename = os.path.join(self.dist_dir, source_rpm)
                self.distribution.dist_files.append(
                    ('bdist_rpm', pyversion, filename))

            if not self.source_only:
                for rpm in binary_rpms:
                    rpm = os.path.join(rpm_dir['RPMS'], rpm)
                    if os.path.exists(rpm):
                        self.move_file(rpm, self.dist_dir)
                        filename = os.path.join(self.dist_dir,
                                                os.path.basename(rpm))
                        self.distribution.dist_files.append(
                            ('bdist_rpm', pyversion, filename))
