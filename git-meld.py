import optparse
import path
import git
import tempfile
import subprocess

def get_parser():
    parser = optparse.OptionParser(
        usage="%prog [revision] [file path]"
    )
    return parser
    

if __name__ == '__main__':
    parser = get_parser()
    (opts, args) = parser.parse_args()
    file_path = args[1]
    repo = git.Repo('.')
    rev = repo.commits(args[0], 1)[0]

    try:
        item = rev.tree
        for n in file_path.split('/'):
            item = item[n]
    except KeyError:
        print "Error: file path %r does not exist in revision %r" % (file_path, revision)

    temp_file = tempfile.NamedTemporaryFile()
    temp_file.write(item.data)
    
    sp = subprocess.Popen(['meld', temp_file.name, file_path])
    sp.wait()
    
    temp_file.close()
    
