# *obf* - an obfuscation tool and library

*obf* is designed to obfuscate an input document, whilst ensuring that the output is still (somewhat) human-readable and 
while also maintaining consistency of mapping between an input plaintext and an obfuscated output, such that 
obf(plaintext) always yields the same result.

This latter characteristic means that *obf* is not really suitable for strong encryption, as frequency analysis of the 
output ciphertext, perhaps with the assistance of a crib, could make the output comprehensible to an attacker.

The intent of *obf* is to allow the sharing of potentially sensitive data outside of a protected zone while ensuring 
it's continued consistency, and thus operability without requiring any changes to other tools and tooling.

*obf* was developed as a tool to allow the copying of data (files and databases) from a protected "green" network to 
unprotected "red" zones, including developer workstations and laptops while maintaining reasonable data privacy. *obf* 
is intended to be used either as a standalone tool or as a library in an automated data-copy process.  

**Installation instructions**
-----------------------------
*obf* is written in Python, and you can use the pip installer to install it thus:

```
$ pip install obf
```

**Usage**
---------
```
obf [-h] [-b [blockedwords file]] [-w [codewords file]] [-c]
                      [-n [N]] [-e [E]] [-a [ALGO]] [-s [SALT]] [-l] [-v]
                      [plaintext]

```

#### positional arguments:

  ```plaintext```       A plaintext to obfuscate. If no plaintext is provided,
                        then obf will look at stdin instead.

#### optional arguments:

```-h, --help```        Show this help message and exit
  
```-b [blockedwords file]```
                        A file containing specific words to block. If missing
                        the entire input is obfuscated.
                        
```-w [codewords file]```
                        A file containing code words to use.
  
```-c ```               Display a crib showing the mapping of blocked values
                        to their obfuscated values. Only works when a specific
                        blockfile is used with the -b option.
                        
```-n [N]```            An index to indicate which bytes of the generated hash
                        to use as a lookup into the codewords file. Defaults
                        to 0.
                        
```-e [E]```            A string of comma-separated domain name components
                        that should be exempt from obfuscation to aid
                        readability. Dots are not permitted/valid. Defaults to
                        'com,co,uk,org' and any that are specified on the
                        command line are added to this list.
                        
```-a [ALGO], --algo [ALGO]```
                        The hash algorithm to use as a basis for indexing the
                        codewords file; defaults to SHA256
                        
```-s [SALT], --salt [SALT]```
                        A salt for the hash function to ensure uniqueness of
                        encoding.
                        
```-l, --list-algos``` List available hash algorithms.

```-j [JSON], --json [JSON]```
                        Treat the input as JSON, and apply the obfuscation
                        rules to each of the fields/keys specified in this
                        space-delimited list

 
```-v ```               Verbose mode = show key parameters, etc




**Examples**
------------

```
$ obf hello
SPRIGHTFUL

```
```
$ cat plaintext.txt | obf
LITHARGE LUNE FELINES PROPHECY FORBORNE ANKLUNGS SPAMS VOYAGE WIVERNS. OUBLIETTES RESTRICTIONS, TRIPTYCHS DREAMING BOLETUS STIRRING THYME BURK TWINS FELINES FRETS PEMMICAN.
STUBBORNNESS HANKERS'BACKSWORD GIFTS ANKLUNGS RIDER PICA RECTA DREAMING@CORPULENCE.TACHOGRAMS BOLETUS STIRRING@CORPULENCE.TACHOGRAMS BLUNGER GIBUSES REPLETES WIVERNS.
LITHARGE SLOTTERS ELUDE DIPODIES GABFESTS EXORCISM URCHIN SOLUTE UNEARTHS PRUNES, BOLETUS STRAFE GABFESTS. "DREAMING", "STIRRING". DREAMING'UPRISE ASPHALTS. STIRRING
DREAMING STIRRING.

LITHARGE SLOTTERS GAMB LODGED PICA BAWL TRANSACTORS ROUTINISTS: PIXELS.JUMBLER@CONNECTORS.TACHOGRAMS ANKLUNGS BANTENG COENZYME GIBUSES FLOCKS.


```
```
$ cat plaintext.txt | obf -b blockedwords.txt 
This is a sample file that holds some secrets. For example, both DREAMING and STIRRING are examples of a FRETS PEMMICAN.
Similarly you'd expect that their email addresses DREAMING@CORPULENCE.com and STIRRING@CORPULENCE.com should be considered secrets.
This line just confims behaviour with preceding or following punctuation, and EOL behaviour. "DREAMING", "STIRRING". DREAMING's house. STIRRING
DREAMING STIRRING.

This line has another email address in it: PIXELS.JUMBLER@CONNECTORS.com that ought to be obfuscated.


```
```
$ cat plaintext.txt | obf -b blockedwords.txt -n23
This is a sample file that holds some secrets. For example, both RETENE and GIBLETS are examples of a SACCHAROID CLEAVE.
Similarly you'd expect that their email addresses RETENE@TEMPERS.com and GIBLETS@TEMPERS.com should be considered secrets.
This line just confims behaviour with preceding or following punctuation, and EOL behaviour. "RETENE", "GIBLETS". RETENE's house. GIBLETS
RETENE GIBLETS.

This line has another email address in it: UNREELS.CLEEKS@UPBEARS.com that ought to be obfuscated.


```
```
$ cat plaintext.txt | obf -b blockedwords.txt -n23 -e bobandsue
This is a sample file that holds some secrets. For example, both RETENE and GIBLETS are examples of a SACCHAROID CLEAVE.
Similarly you'd expect that their email addresses RETENE@bobandsue.com and GIBLETS@bobandsue.com should be considered secrets.
This line just confims behaviour with preceding or following punctuation, and EOL behaviour. "RETENE", "GIBLETS". RETENE's house. GIBLETS
RETENE GIBLETS.

This line has another email address in it: UNREELS.CLEEKS@UPBEARS.com that ought to be obfuscated.


```
```
$ cat plaintext.txt | obf -b blockedwords.txt -n23 -e bobandsue -v -c
{'blockedwords': ['secret', 'name', 'bob', 'sue'], 'hash_index': 23, 'hash_index_length': 4, 
'codewords_file': '/Users/hossein/anaconda3/lib/python3.6/site-packages/obf/codewords.txt', 
'codewords_hash': '25e011f81127ec5b07511850b3c153ce6939ff9b96bc889b2e66fb36782fbc0e', 
'excluded_domains': ['com', 'org', 'co', 'uk', 'bobandsue'], 'codewords_length': 66740}
secret -> SACCHAROID
name -> CLEAVE
bob -> RETENE
sue -> GIBLETS
```

```
obf -b blockedwords.txt -c -v -n23 --algo MD5 --salt examplesalt
{'codewords_hash': '25e011f81127ec5b07511850b3c153ce6939ff9b96bc889b2e66fb36782fbc0e', 'salt': 'examplesalt',
 'hash_index_length': 4, 'hash_algo': 'MD5', 'excluded_domains': ['com', 'org', 'co', 'uk'], 'hash_index': 12, 
 'codewords_file': '../obf/codewords.txt', 'blockedwords': ['secret', 'name', 'bob', 'sue'], 
 'codewords_length': 66740}
secret -> REVEALMENT
name -> LOBATE
bob -> ZOMBIS
sue -> DEIL
```

**Homepage**
------------

You can find the homepage of *obf* at https://github.com/hossg/obf