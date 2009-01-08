import optparse
import os
import git
import tempfile
import subprocess

def get_parser():
    parser = optparse.OptionParser(
        usage="""%prog [OPTION] REVISION FILE

Will compare FILE with the same file at REVISION."""
    )
    parser.add_option("-d", "--difftool", default="meld", help="command to produce diff")
    parser.add_option("-r", "--repo_path", default=".", help="path of repository")
    return parser
    

if __name__ == '__main__':
    parser = get_parser()
    (opts, args) = parser.parse_args()
    revision, file_path = args
    
    try:
        repo = git.Repo(opts.repo_path)
    except git.errors.InvalidGitRepositoryError:
        parser.error("path %r is not a git repository" % (opts.repo_path))

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

    if not os.path.exists(file_path):
        parser.error("cannot find current version of file %r" % (file_path))

    temp_file = tempfile.NamedTemporaryFile(suffix=os.path.splitext(file_path)[1])
    temp_file.write(item.data)
    
    try:
        sp = subprocess.Popen([opts.difftool, temp_file.name, file_path])
        sp.wait()
    except OSError:
        parser.error("are you sure %r is a valid diff tool?" % (opts.difftool))
    
    temp_file.close()
