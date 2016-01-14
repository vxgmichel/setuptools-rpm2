"""Provide the setuptools command sdist2."""

import os
from distutils import dir_util
from setuptools.command.sdist import sdist


class sdist2(sdist):

    # Description
    description = "modified version of sdist"

    # Copy user options
    user_options = list(sdist.user_options)

    # Add name-prefix option
    user_options.append((
        'dist-prefix=', None,
        "Add a prefix to the distribution name (joined with '-')"))

    def initialize_options(self):
        self.dist_prefix = ''
        sdist.initialize_options(self)

    def finalize_package_data(self):
        self.ensure_string('dist_prefix')
        self.dist_prefix = self.dist_prefix.rstrip('-')
        sdist.finalize_package_data(self)

    def add_dist_prefix(self, name):
        if not self.dist_prefix:
            return name
        return '-'.join((self.dist_prefix, name))

    # The rest of the file is shamelessly copied from
    # distutils/command/sdist.py. The only modifications are:
    # - the declaration of the `base_dir` variable, where the distribution
    # name is prefixed using the corresponding user option

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
        base_dir = self.add_dist_prefix(self.distribution.get_fullname())
        base_name = os.path.join(self.dist_dir, base_dir)

        self.make_release_tree(base_dir, self.filelist.files)
        archive_files = []              # remember names of files we create
        # tar archive must be created last to avoid overwrite and remove
        if 'tar' in self.formats:
            self.formats.append(self.formats.pop(self.formats.index('tar')))

        for fmt in self.formats:
            file = self.make_archive(base_name, fmt, base_dir=base_dir,
                                     owner=self.owner, group=self.group)
            archive_files.append(file)
            self.distribution.dist_files.append(('sdist', '', file))

        self.archive_files = archive_files

        if not self.keep_temp:
            dir_util.remove_tree(base_dir, dry_run=self.dry_run)
