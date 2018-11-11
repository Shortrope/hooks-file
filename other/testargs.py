from optparse import OptionParser

parser = OptionParser()

parser.add_option("-v", "--verbose",
                    help="Display verbose output")
parser.add_option("-p", "--port",
                    dest="port",
                    type="int",
                    default=80,
                    help="Port number. e.g. 80")

(options, args) = parser.parse_args()

print("Options:")
print(options)
print("args:")
print(args)