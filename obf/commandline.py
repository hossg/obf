import obf
import argparse, hashlib,sys,os, demjson
import proxy
import configargparse



def main():

    parser = configargparse.ArgumentParser(
        description="obf - an obfuscation tool",
        epilog="More information/homepage: https://github.com/hossg/obf",
        default_config_files=['/etc/obf.conf', '~/.obf'])

    # command line only arguments that are relevant only for "interactive" use of the tool
    parser.add('--config', required=False, is_config_file=True, help='Config file path')
    parser.add_argument('plaintext',nargs="?", help="A plaintext to obfuscate. If no plaintext is provided, then obf " \
                                                    "will look at stdin instead.")
    parser.add_argument('-c', action="store_true", default=False, help="Display a crib showing the mapping of blocked " \
                                                                       "values to their obfuscated values.  Only works " \
                                                                       "when a specific blockfile is used with the -b " \
                                                                       "option.")

    parser.add_argument('-l', '--list-algos', action="store_true", help="List available hash algorithms.")

    parser.add_argument('-v', action="store_true", help="Verbose mode = show key parameters, etc")

    parser.add_argument('--proxy', nargs=1, help = "A hostname and port to proxy for")

    parser.add_argument('-j','--json', nargs='?', help = "Treat the input as JSON, and apply the obfuscation rules to "\
                        "each of the fields/keys specified in this space-delimited list")
    # arguments for config file, environment variables or config file, useful for configuring the obfuscator


    parser.add_argument('-b', '--blockedwords', metavar='blockedwords file',nargs='?', help="A file containing specific words to block. " \
                                                                        "If missing the entire input is obfuscated.")
    parser.add_argument('-w', metavar='codewords file', nargs='?',
                        default=os.path.dirname(__file__)+'/'+"codewords.txt",
                        help="A file containing code words to use. ")

    parser.add_argument('-n','--n_offset', type=int,default=0,nargs='?', help="An index to indicate which bytes of the generated hash " \
                                                                "to use as a lookup into the codewords file. Defaults "
                                                                "to 0.")
    parser.add_argument('-e', nargs='?',
                        help="A string of comma-separated domain name components that should be exempt from obfuscation"\
                        " to aid readability. Dots are not permitted/valid. Defaults to 'com,co,uk,org' and any that "\
                        "are specified on the command line are added to this list.")

    parser.add_argument('-a','--algo', nargs='?',default="SHA256",
                        help="The hash algorithm to use as a basis for indexing the codewords file; defaults to SHA256")

    parser.add_argument('-s','--salt', nargs='?', default='',
                        help="A salt for the hash function to ensure uniqueness of encoding.")



    args=parser.parse_args()

    if args.list_algos:
        print(sorted(hashlib.algorithms_available))
        quit()


    codewords_file=args.w
    excluded_domains = ['com', 'org', 'co', 'uk']
    if (parser.parse_args().e):
        for i in parser.parse_args().e.split(','):
            excluded_domains.append(i.strip())


    # Is a blockedwords file provided?
    blockedwords=[]
    if args.blockedwords:
        with open(args.blockedwords) as f:
            lines = f.read().splitlines()
            for line in lines:
                for word in line.split():
                    blockedwords.append(word.strip())
    else:
        blockedwords=False

    o = obf.obfuscator(algo=args.algo,
                       salt=args.salt,
                       blockedwords=blockedwords,
                       hash_index=args.n_offset,
                       hash_index_length=4,
                       codewords_file=codewords_file,
                       codewords_hash='25e011f81127ec5b07511850b3c153ce6939ff9b96bc889b2e66fb36782fbc0e',
                       # TODO remove this from the constructor, as we should really be able to rely on the core package for the DEFAULT codewords hash value

                       excluded_domains=excluded_domains)

    d=o.describe()
    # Verbose mode?
    if args.v:
        print(d)

    # and if so, is a crib sheet required?
    if (blockedwords and args.c):
        for entry in blockedwords:
            s = []
            for item in entry.split():
                s.append(o.encode(item))

            print("{} -> {}".format(entry, ' '.join(s)))
        quit()


    # is some plaintext provided directly on the command line?
    if args.plaintext:
        print(' '.join(map(o.encode_text,args.plaintext.split())))
    # else take plaintext from stdin, line at a time
    elif args.json:

        j=''
        for line in sys.stdin:
            j = j + line
        j = demjson.decode(j)
        j = demjson.encode(j,compactly=False)       # do our best to make the JSON valid and presentable

        print(demjson.encode(o.encode_json(j,args.json.split()),compactly=False))
    elif args.proxy:
        proxy.main(['--enable-web-server','--plugin', 'obf.obf_reverse_proxy'])
    else:
        for line in sys.stdin:
            line=line[:-1]
            print(o.encode_text(line))


# Command line behaviour
if __name__=='__main__':
    main()