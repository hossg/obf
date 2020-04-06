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
import os
import json


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

DEFAULT_ALGO = "SHA256"
DEFAULT_SALT = ''
DEFAULT_BLOCKEDWORDS = None
DEFAULT_CODEWORDS_FILE = codewords_file = os.path.dirname(__file__) + '/' + "codewords.txt"
DEFAULT_HASH_INDEX_OFFSET = 0
DEFAULT_IGNORED_EMAIL_DOMAINS = ['com', 'org', 'co', 'uk']
DEFAULT_HASH_INDEX_LENGTH = 4
DEFAULT_CODEWORDS_HASH ='25e011f81127ec5b07511850b3c153ce6939ff9b96bc889b2e66fb36782fbc0e'

class obfuscator:

    def __init__(self, algo=DEFAULT_ALGO,salt=DEFAULT_SALT,blockedwords=DEFAULT_BLOCKEDWORDS,
                 hash_index=DEFAULT_HASH_INDEX_OFFSET, hash_index_length=DEFAULT_HASH_INDEX_LENGTH,
                 codewords_file=DEFAULT_CODEWORDS_FILE,
                 codewords_hash=DEFAULT_CODEWORDS_HASH,
                 excluded_domains=DEFAULT_IGNORED_EMAIL_DOMAINS):

        self.excluded_domains=excluded_domains
        self.p=hash_index_length
        self.n=hash_index           # The default position in the hash string to use as a lookup into the codewords list
        self.salt = salt
        self.hash_algo = hashlib.new(algo)
        if self.n < 0:
            self.n = 0
        if self.n > (self.hash_algo.digest_size - self.p):
            self.n = self.hash_algo.digest_size - self.p

        self.blockedwords=blockedwords    # A list of words we want to explicitly block

        self.codewords_file=codewords_file
        self.codewords_hash=codewords_hash
        if self.__check_integrity():
            self.codewords = self.load_codewords(codewords_file)

    def describe(self):
        return {
            'hash_algo' : self.hash_algo.name,
            'salt' : self.salt,
            'blockedwords' : self.blockedwords,
            'hash_index':self.n,
            'hash_index_length':self.p,
            'codewords_file':self.codewords_file,
            'codewords_hash':self.codewords_hash,
            'excluded_domains':self.excluded_domains,
            'codewords_length':len(self.codewords)

        }

    def load_codewords(self,filename):
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
    def __check_integrity(self):
        with open(self.codewords_file,'rb') as binary_file:
            h = hashlib.sha256()    # The integrity check is always based upon a SHA256 fingerprint, it's
                                    # unrelated to the hashing used for the core obf functionality
            while True:
                data = binary_file.read(2 ** 20)
                if not data:
                    break
                h.update(data)

            assert h.hexdigest() == self.codewords_hash,\
                                    "Codeword file has been tampered with."
            return True

    # Encode a string
    # This algorithm is case-insensitive in order to ensure easy, human-level consistency across plaintext and ciphertext.
    def encode(self,s):
        s=self.salt+s                       # TODO - should probably move this to the the stored hasher, before it's repeatedly copied
        bytes = s.upper().encode('utf-8')
        a=self.hash_algo.copy()
        a.update(bytes)
        h = a.hexdigest()[self.n:self.n+self.p]    # use the 4 bytes from position n in the hash
        d = int(h, 16)                                  # as an index into the codeword table
        i = d % len(self.codewords)                          # wrap to ensure we always return a value, in case the codeword
                                                        # file is too short. This would break 1->1 mapping of plaintext
                                                        # to ciphertext, but is "less worse" than not returning anything!
                                                        # The solution is to ensure you have more available codewords
                                                        # than you actually need!
        w = self.codewords[i]
        return w.upper()

    # Encode an email address
    # A utility function to encode an email address, trivially trying to encode the bits before the @ symbol, and
    # (by default) also the domain components, with the exception of some pre-defined domains, in order to make the
    # resulting obfuscation still resemble an email address (for readability purposes).
    def encode_email(self,e,includeDomain=True):
        name, domain = e.split('@')
        names = name.split('.')
        newNames=[]
        for n in names:
            newNames.append(self.encode(n))
        newName='.'.join(newNames)
        if includeDomain==False:
            return newName+'@'+domain


        domains = domain.split('.')
        newDomains = []
        for d in domains:
            if d not in self.excluded_domains:
                newDomains.append(self.encode(d))
            else:
                newDomains.append(d)
        newDomain = '.'.join(newDomains)
        return newName+'@'+newDomain

    # A utility function to take a string (actually a regex match group) and see if it looks like an email address, and
    # if so encode it according to the special email encoding rule above, else simply encode it normally.
    def __encodedReplacement(self,match):
        if '@' in match.group():
            return self.encode_email(match.group())
        else:
            return self.encode(match.group())

    # Encode some text
    def encode_text(self,t):

        if not self.blockedwords:        # if there are no specifically-defined blockedwords then obfuscate every word
            r = r'[a-zA-Z]+'

                                    # otherwise obfuscate only specific blockwords, and also anything that looks like an
                                    # email address.
        else:
            r = r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)|" # and anything that looks like an email address

            for entry in self.blockedwords:
                for item in entry.split():
                    r = r + r'\b' + item + r'\b|'
            r = r[:-1]


        rr = re.compile(r, re.IGNORECASE)
        t = rr.sub(self.__encodedReplacement,t)
        return t


    def encode_list(self, l):
        """Recursively encodes all string elements in a list"""

        m = [self.encode_text(i) if type(i) is str else i for i in l]
        n = [self.encode_list(i) if type(i) is list else i for i in m]
        return n

    def __encode_selected_key(self,d):
        """Encodes all string values and list values in a dict, if the key is part of the seclector defined by
        this obfuscator"""

        for k in self.selected_keys:
            if k in d:
                if type(d[k]) is str:
                    d[k]=self.encode_text(d[k])
                if type(d[k]) is list:
                    d[k]=self.encode_list(d[k])
        return d

    def encode_json(self, s, selected_keys):
        """Given a json document as a string, and a set of selected keys to obfuscate, this will return an object with
        the values of those keys obfuscated
        """

        self.selected_keys=selected_keys
        x=json.loads(s, object_hook=self.__encode_selected_key)
        return x


