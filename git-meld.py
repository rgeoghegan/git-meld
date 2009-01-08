#!/usr/bin/env python
import optparse
import os
import git
import tempfile
import subprocess

def get_parser():
    parser = optparse.OptionParser(
        usage="""%prog [OPTION] REVISION [REVISION2] FILE

Will compare FILE with the same file at REVISION. If REVISION2 is not given, compares to file in working directory."""
    )
    parser.add_option("-d", "--difftool", default="meld", help="command to produce diff")
    parser.add_option("-r", "--repo_path", default=".", help="path of repository")
    return parser

def fetch_from_revision(revision, file_path, parser):
    """Throws git.errors.GitCommandError if revision is not a valid revision reference. Throws KeyError if file_path does not exists at revision. Returns temporary file handle."""
    try:
        rev = repo.commits(args[0], 1)[0]
    except git.errors.GitCommandError:
        parser.error("%r is not a valid revision reference" % (revision))

    try:
        item = rev.tree
        for n in file_path.split('/'):
            item = item[n]
    except KeyError:
        parser.error("file path %r does not exist in revision %r" % (file_path, revision))

    temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(file_path)[1])
    temp_file.write(item.data)
    return temp_file

def launch_diff(difftool, file1, file2, parser):
    """Launches a diff of the two file paths with specified difftool."""
    try:
        sp = subprocess.Popen([difftool, file1, file2])
        sp.wait()
    except OSError:
        parser.error("are you sure %r is a valid diff tool?" % (opts.difftool))
        

if __name__ == '__main__':
    parser = get_parser()
    (opts, args) = parser.parse_args()

    try:
        repo = git.Repo(opts.repo_path)
    except git.errors.InvalidGitRepositoryError:
        parser.error("path %r is not a git repository" % (opts.repo_path))

    temp_file_1 = fetch_from_revision(args[0], args[-1], parser)

    if len(args) == 3:
        temp_file_2 = fetch_from_revision(args[1], args[-1], parser)
        launch_diff(opts.difftool, temp_file_1.name, temp_file_2.name, parser)
        temp_file_2.close()
    else:
        if not os.path.exists(args[-1]):
            parser.error("cannot find file %r in working directory" % (args[-1]))
        launch_diff(opts.difftool, temp_file_1.name, args[-1], parser)

    temp_file_1.close()
