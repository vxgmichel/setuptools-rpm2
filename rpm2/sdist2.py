"""Provide the setuptools command sdist2."""

import os
from distutils import dir_util
from setuptools.command.sdist import sdist


class sdist2(sdist):
    """Add two extra user options to the setuptools bdist_rpm command:
     --dist-name: specify a different distribution name
     --add-test: add 'python setup.py test' to the %check section
    """

    # Description
    description = "modified version of sdist"

    # Copy user options
    user_options = list(sdist.user_options)

    # Add name-prefix option
    user_options.append((
        'dist-name=', None,
        "Specify a different distribution name"))

    def initialize_options(self):
        self.dist_name = ''
        sdist.initialize_options(self)

    def finalize_package_data(self):
        self.ensure_string('dist_name')
        self.dist_name = self.dist_name.strip()
        sdist.finalize_package_data(self)

    @property
    def distribution_name(self):
        if self.dist_name:
            return self.dist_name
        return self.distribution.get_name()

    # The rest of the file is shamelessly copied from
    # distutils/command/sdist.py. The only modifications are:
    # - the declaration of the `base_dir` variable, where the distribution
    # name is prefixed using the corresponding user option
    # - use `self.owner` and `self.group` if they exist (python 2.6
    # compatibility)

    def make_distribution(self):
        """Create the source distribution(s).  First, we create the release
        tree with 'make_release_tree()'; then, we create all required
        archive files (according to 'self.formats') from the release tree.
        Finally, we clean up by blowing away the release tree (unless
        'self.keep_temp' is true).  The list of archive files created is
        stored so it can be retrieved later by 'get_archive_files()'.
        """
        # Don't warn about missing meta-data here -- should be (and is!)
        # done elsewhere.
        base_dir = self.distribution_name
        base_name = os.path.join(self.dist_dir, base_dir)

        self.make_release_tree(base_dir, self.filelist.files)
        archive_files = []              # remember names of files we create
        # tar archive must be created last to avoid overwrite and remove
        if 'tar' in self.formats:
            self.formats.append(self.formats.pop(self.formats.index('tar')))

        for fmt in self.formats:
            try:
                kwargs = {'owner': self.owner, 'group': self.group}
            except AttributeError:
                kwargs = {}
            file = self.make_archive(base_name, fmt, base_dir=base_dir,
                                     **kwargs)
            archive_files.append(file)
            self.distribution.dist_files.append(('sdist', '', file))

        self.archive_files = archive_files

        if not self.keep_temp:
            dir_util.remove_tree(base_dir, dry_run=self.dry_run)
