import obf
import argparse, hashlib,sys,os



def main():

    parser = argparse.ArgumentParser(
        description="obf - an obfuscation tool",
        epilog="More information/homepage: https://github.com/hossg/obf'")
    parser.add_argument('plaintext',nargs="?", help="A plaintext to obfuscate. If no plaintext is provided, then obf " \
                                                    "will look at stdin instead.")
    parser.add_argument('-b',metavar='blockedwords file',nargs='?', help="A file containing specific words to block. " \
                                                                        "If missing the entire input is obfuscated.")
    parser.add_argument('-w', metavar='codewords file', nargs='?',
                        default=os.path.dirname(__file__)+'/'+"codewords.txt",
                        help="A file containing code words to use. ")

    parser.add_argument('-c',action="store_true",default=False,help="Display a crib showing the mapping of blocked "\
                                                                    "values to their obfuscated values.  Only works "\
                                                                    "when a specific blockfile is used with the -b "\
                                                                    "option.")
    parser.add_argument('-n',type=int,default=0,nargs='?', help="An index to indicate which bytes of the generated hash " \
                                                                "to use as a lookup into the codewords file. Defaults "
                                                                "to 0.")
    parser.add_argument('-e', nargs='?',
                        help="A string of comma-separated domain name components that should be exempt from obfuscation"\
                        " to aid readability. Dots are not permitted/valid. Defaults to 'com,co,uk,org' and any that "\
                        "are specified on the command line are added to this list.")
    parser.add_argument('-v', action="store_true", help="Verbose mode = show key parameters, etc" )


    args=parser.parse_args()

    # Firstly deal with setting the N value to be different to the default.

    codewords_file=args.w

    excluded_domains = ['com', 'org', 'co', 'uk']
    if (parser.parse_args().e):
        for i in parser.parse_args().e.split(','):
            excluded_domains.append(i.strip())


    # Is a blockedwords file provided?
    blockedwords=[]
    if args.b:
        with open(args.b) as f:
            lines = f.read().splitlines()
            for line in lines:
                for word in line.split():
                    blockedwords.append(word.strip())
    else:
        blockedwords=False

    o = obf.obfuscator(blockedwords=blockedwords,
                       hash_index=args.n,
                       hash_index_length=4,
                       codewords_file=codewords_file,
                       codewords_hash='25e011f81127ec5b07511850b3c153ce6939ff9b96bc889b2e66fb36782fbc0e',
                       excluded_domains=excluded_domains)

    d=o.describe()
    # Verbose mode?
    if (parser.parse_args().v):
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
    else:
        for line in sys.stdin:
            line=line[:-1]
            print(o.encode_text(line))


def test():
    print('This is a test')
    print(obf)

# Command line behaviour
if __name__=='__main__':
    main()