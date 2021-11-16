import sys
import getopt
args = args[1:]
print(args)
shortopts = "d:v:g:f:"
longopts = ['doi', 'dvtoken', 'ghtoken', 'folder']
options, args = getopt.getopt(args, shortopts, longopts)

print(args)
