#!/usr/bin/python3

# obf - an obfuscation tool and library
# Copyright (C) 2018 Hossein Ghodse
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import hashlib
import re
import argparse
import sys

# requirements:
# 1. a plaintext word always maps to the same codeword
# 2. it is extremely unlikely that two different plaintext words map to the same codeword
# 3. it is extremely difficult to reverse-engineer a plaintext word from a codeword without a crib

# Firstly we clearly need more codewords available to choose from than we have plaintext words.
# We achieve this by taking a one-way hash of the plaintext, and choosing the last n digits of this as the "effective
# hash".  We then use this "effective hash" as a lookup into a list of codewords.  We employ modulus looping to ensure
# that we can always return a codeword, but this is a safety precaution only as any modulus looping increases the
# likelihood of a collision of codewords.  As long as we have more codewords available than the length of the effective
# hash permits, we can avoid this increase in collision probability. If we have a dictionary of >=65535 codewords, then
# we should pick our effective hash to be 4 bytes long.


excluded_domains=[]
p=4
n=0                 # The default position in the hash string to use as a lookup into the codewords list
blockedwords=[]     # A list of words we want to explicitly block
codewords=None
def load_codewords(filename):
    with open(filename) as f:
        codewords = f.read().splitlines()
    l=len(codewords)
    p=0
    while 16**p < l:
        p=p+1
    p=p-1   # p is the number of bytes we need to pick out of a generated hash of a plaintext to index into the
            # codewords file.  We want the maximum p that is less than the number of entries in the codeword file.
    return codewords

# Test the integrity of the codeword file.
# Clearly this does prevent editing the codeword file AND this file, but it allows for managing accidental edits to the
# codeword file, and also allows publication of the  hash key below, which can allow independent verification of the
# codeword file.  This doesn't provide any increase in security, but it does help ensure consistent obfuscation which
# is an important characteristic of the package.
def check_integrity(filename):
    with open('codewords.txt','rb') as binary_file:
        h = hashlib.sha256()
        while True:
            data = binary_file.read(2 ** 20)
            if not data:
                break
            h.update(data)

        assert h.hexdigest() == '25e011f81127ec5b07511850b3c153ce6939ff9b96bc889b2e66fb36782fbc0e',\
                                "Codeword file has been tampered with."
        return h.hexdigest()

# Encode a string
# This algorithm is case-insensitive in order to ensure easy, human-level consistency across plaintext and ciphertext.
def encode(s):
    bytes = s.upper().encode('utf-8')
    h = hashlib.sha256(bytes).hexdigest()[n:n+p]    # use the 4 bytes from position n in the hash
    d = int(h, 16)                                  # as an index into the codeword table
    i = d % len(codewords)                          # wrap to ensure we always return a value, in case the codeword
                                                    # file is too short. This would break 1->1 mapping of plaintext
                                                    # to ciphertext, but is "less worse" than not returning anything!
                                                    # The solution is to ensure you have more available codewords
                                                    # than you actually need!
    w = codewords[i]
    return w.upper()

# Encode an email address
# A utility function to encode an email address, trivially trying to encode the bits before the @ symbol, and
# (by default) also the domain components, with the exception of some pre-defined domains, in order to make the
# resulting obfuscation still resemble an email address (for readability purposes).
def encode_email(e,includeDomain=True):
    name, domain = e.split('@')
    names = name.split('.')
    newNames=[]
    for n in names:
        newNames.append(encode(n))
    newName='.'.join(newNames)
    if includeDomain==False:
        return newName+'@'+domain


    domains = domain.split('.')
    newDomains = []
    for d in domains:
        if d not in excluded_domains:
            newDomains.append(encode(d))
        else:
            newDomains.append(d)
    newDomain = '.'.join(newDomains)
    return newName+'@'+newDomain

# A utility function to take a string (actually a regex match group) and see if it looks like an email address, and
# if so encode it according to the special email encoding rule above, else simply encode it normally.
def encodedReplacement(match):
    if '@' in match.group():
        return encode_email(match.group())
    else:
        return encode(match.group())

# Encode some text
def encode_text(t):

    if not blockedwords:        # if there are no specifically-defined blockedwords then obfuscate every word
        r = r'[a-zA-Z]+'

                                # otherwise obfuscate only specific blockwords, and also anything that looks like an
                                # email address.
    else:
        r = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)|" # and anything that looks like an email address

        for entry in blockedwords:
            for item in entry.split():
                r = r + r'\b' + item + r'\b|'
        r = r[:-1]


    rr = re.compile(r, re.IGNORECASE)
    t = rr.sub(encodedReplacement,t)
    return t



# Command line behaviour
if __name__=='__main__':

    check_integrity("codewords.txt")

    parser = argparse.ArgumentParser(
        description="obf - an obfuscation tool",
        epilog="If no plaintext is provided, then obf will look at stdin instead.")
    parser.add_argument('plaintext',nargs="?", help="A plaintext to obfuscate.")
    parser.add_argument('-b',metavar='blockedwords file',nargs='?', help="A file containing specific words to block. " \
                                                                        "If missing the entire input is obfuscated.")
    parser.add_argument('-w', metavar='codewords file', nargs='?', default="codewords.txt",help="A file containing code"\
                                                                            "words to use. ")

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

    # Firstly deal with setting the N value to be different to the default.
    n=parser.parse_args().n
    if n<0:
        n=0
    if n>(hashlib.sha256().digest_size-p):
        n=hashlib.sha256().digest_size-p

    codewords=load_codewords(parser.parse_args().w)

    excluded_domains = ['com', 'org', 'co', 'uk']
    if (parser.parse_args().e):
        for i in parser.parse_args().e.split(','):
            excluded_domains.append(i.strip())

    # Verbose mode?
    if(parser.parse_args().v):
        print("starting index in hash to use as index={}; number of bytes from hash to use as index={}; entries in "
              "codeword file={};\n"\
              "excluded domains:{}\n".format(n,p,len(codewords),excluded_domains))



    # Is a blockedwords file provided?
    if(parser.parse_args().b):
        with open(parser.parse_args().b) as f:
            lines = f.read().splitlines()
            for line in lines:
                for word in line.split():
                    blockedwords.append(word.strip())

        # and if so, is a crib sheet required?
        if (parser.parse_args().c):
            for entry in blockedwords:
                s = []
                for item in entry.split():
                    s.append(encode(item))

                print("{} -> {}".format(entry, ' '.join(s)))
            quit()
    else:
        blockedwords=False

    # is some plaintext provided directly on the command line?
    if(parser.parse_args().plaintext):
        print(' '.join(map(encode_text,parser.parse_args().plaintext.split())))
    # else take plaintext from stdin, line at a time
    else:
        for line in sys.stdin:
            line=line[:-1]
            print(encode_text(line))

