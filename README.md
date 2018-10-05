#*obf* - an obfuscation tool and library

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

**Usage**
---------
`obf.py [-h] [-b [blockedwords file]] [-c [C]] [-n [N]] [plaintext]`



*positional arguments:*

`plaintext`            A plaintext to obfuscate.

*optional arguments:*

`  -h, --help `           show this help message and exit

`  -b [blockedwords file]`
                        A file containing specific words to block. If missing
                        the entire input is obfuscated.
                        
`  -c [C] `              Display a crib showing the mapping of blocked values
                        to their obfuscated values. Only works when a specific
                        blockfile is used with the -b option.
                        
  `-n [N]`              An index to indicate which bytes of the generated hash
                        to use as a lookup into the codewords file. Defaults
                        to 4.

If no plaintext is provided, then obf will look at stdin instead.

**Examples**
------------
```
$ ./obf.py hello 
SPRIGHTFUL
$
```

```

$ cat plaintext.txt | ./obf.py
LITHARGE LUNE FELINES PROPHECY FORBORNE ANKLUNGS SPAMS VOYAGE WIVERNS. OUBLIETTES RESTRICTIONS TRIPTYCHS DREAMING BOLETUS STIRRING THYME BURK TWINS FELINES FRETS PEMMICAN.
STUBBORNNESS HANKERS'BACKSWORD GIFTS ANKLUNGS RIDER PICA RECTA DREAMING@CORPULENCE.TACHOGRAMS BOLETUS STIRRING@CORPULENCE.TACHOGRAMS BLUNGER GIBUSES REPLETES WIVERNS.
LITHARGE SLOTTERS ELUDE DIPODIES GABFESTS EXORCISM URCHIN SOLUTE UNEARTHS PRUNES BOLETUS STRAFE GABFESTS. "DREAMING", "STIRRING". DREAMING
$
```
```
$ cat plaintext.txt | ./obf.py -b blockedwords.txt
This is a sample file that holds some secrets. For example both DREAMING and STIRRING are examples of a secret PEMMICAN.
Similarly you'd expect that their email addresses DREAMING@CORPULENCE.com and STIRRING@CORPULENCE.com should be considered secrets.
This line just confims behaviour with preceding or following punctuation and EOL behaviour. "DREAMING", "STIRRING". DREAMING
$
```
 ```
 $ cat plaintext.txt | ./obf.py -b blockedwords.txt -n 23
This is a sample file that holds some secrets. For example both RETENE and GIBLETS are examples of a secret CLEAVE.
Similarly you'd expect that their email addresses RETENE@TEMPERS.com and GIBLETS@TEMPERS.com should be considered secrets.
This line just confims behaviour with preceding or following punctuation and EOL behaviour. "RETENE", "GIBLETS". RETENE
$
```

```
$ cat plaintext.txt | ./obf.py -b blockedwords.txt -n 23 -v -e bobandsue
starting index in hash to use as index=23; number of bytes from hash to use as index=4; entries in codeword file=66740;
excluded domains:['com', 'org', 'co', 'uk', 'bobandsue']

This is a sample file that holds some secrets. For example both RETENE and GIBLETS are examples of a secret CLEAVE.
Similarly you'd expect that their email addresses RETENE@bobandsue.com and GIBLETS@bobandsue.com should be considered secrets.
This line just confims behaviour with preceding or following punctuation and EOL behaviour. "RETENE", "GIBLETS". RETENE
$
```
```
$ cat plaintext.txt | ./obf.py -b blockedwords.txt -n 23 -c

secret -> SACCHAROID
name -> CLEAVE
bob -> RETENE
sue -> GIBLETS
```