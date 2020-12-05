# The Shark Cipher

## About the Cipher

The operation of this cipher is outlined in Letter #111 from the First Eric
Sanderson (presented on pages 73--76 of _The Raw Shark Texts_ by Steven Hall).
To use the cipher in the exact manner outlined in the book, the intended
direction needs to be set with the `--encrypt` or `--decipher` flags.

An alternate version is run with the default `--reversible` flag.  In this
variant, only links where the both output and input contain the other in their
surrounding letters are considered.  While both versions can, in theory,
unambiguously reverse back to cleartext if `--fixed` is used instead of the
default `--random`, the differing numbers of valid substitutions per keycap
means that it would be a notably more complicated process than reversing `mod
8` arithmetic. 

The ambiguity of both methods is conceptual shark-repellent, not a bug.
Run `./cipher.py --help` to read about all the various options.

## System Requirements

Python 3.8+ with Click installed (see `requirements.txt`)

## Tutorial

We will encode example phrases on a Dvorak keyboard using both the symmetric
and original ciphers.  Next, we run the ciphertext through the program to show
that the letter of the input are in the possibilities of the output.  Your
exact results will vary due to the random selection of which possibility is
chosen.

### 1. Encode

Note how both commands have a `-` immediately before the file redirection.
That hyphen means that input is read from `stdin` and allows us to pipe
our input.

```
><)> echo "What you are refering to as Linux…" | ./cipher.py -k Dvorak --only-one - > symmetric.swp
><)> cat symmetric.swp
hmqnxqklzocogkcbcdhqslvdvjf
><)> echo "…is, in fact, GNU+Linux." | ./cipher.py -k Dvorak --only-one --encrypt --include - > original.swp
><)> cat original.swp
…fa, uv ylwh, tvp+rxzik
```

As you may guess, using `--include` makes decoding vastly easier by telling
us where the spaces and punctuation reside.

### 2. Decode

Since `.swp` files were created in step 1, we will now use the files for the TEXT
argument in place of the hyphen.  As you may note, the ability to accept
input from `stdin` means you can also do such galaxy-brained things such as
piping in a `cat filename.txt` or using `<` file redirection.

In the following examples, the cleartext has been inserted next to the ciphertext
of the output for demonstration purposes.

```
><)> ./cipher.py -k Dvorak symmetric.swp
hmqnxqklzocogkcbcdhqslvdvjf
whatyouarereferingtoaslinux
---------------------------
wbezpaevrqgqminfgbwzzvchlkd
ttotfzxrlenjdjmghhdenpnxcpy
mdavijupnjhahxwxrxbolarirub
cfzwdepsvawetyhmnicjrntmwem
ghjlbojasqrqcetivggaaslbsoh
dweskayzqevjfugdwyfzvrsfzqi
fgocyzinajmawpvytftezzzgnkg
bcarujevratebirhmmmonvwytpx
---------------------------
whatyouarereferingtoaslinux
hmqnxqklzocogkcbcdhqslvdvjf
```

If you are bored, check that each letter of the original message exists in the
column above it.

```
><)> ./cipher.py -k Dvorak --decipher --include original.swp
…fa, uv ylwh, tvp+rxzik
…is, in fact, GNU+Linux
-----------------------
…dl, lr bvrw, vzy+tdpxy
…gz, yn fqvc, grx+wkvpl
…ho, jz drmm, csk+cfqbi
…xs, et isnd, nni+nulfe
…iq, xc uahb, wcj+lyndp
…bl, ks kpcf, hte+sbakx
…yz, pw xztg, mll+zisuj
…mo, il pngt, rwu+vpryu
-----------------------
…is, in fact, GNU+Linux
…fa, uv ylwh, tvp+rxzik
``` 

Isn't it amazing how much nicer it is to have spaces and punctuation?

### Getting things wrong

The exclamation points in the fencing indicate a non-exhaustive
list of positions where the cleartext letter is not among the options.

#### Decoding with the wrong layout

Decoded using the default QWERTY keyboard after being encoded Dvorak.

```
><)> ./cipher.py symmetric.swp
hmqnxqklzocogkcbcdhqslvdvjf
whatyouarereferingtoaslinux
!---!!--!!-!-!-!!!-!-!!!!-!
jkxbspmisispbirrswjwqifsrig
mhataajpxlxihleyvrmxeaexdht
buzuzxlampektmdvrcbzzorefmv
yisjdwiopkrlnoffxeysapbfcuc
nzwgqzokaivpyjxgfvupxkcwtkd
gypmcsuiwldifuvhestadigcenr
ujxhwpmpqpfkristdfgwcatrbye
tnayeajaskwlvlwnwxnxwodvgib
!---!!--!!-!-!-!!!-!-!!!!-!
whatyouarereferingtoaslinux
hmqnxqklzocogkcbcdhqslvdvjf
```

* Every instance of o, r, e, i, and n is a mismatch—indicates that the letters
  are not linked in the same way
* Due to the large difference between Dvorak and QWERTY, there are more
  mismatches here than a Colemak/QWERTY conflict

#### Using a mismatching direction option

In this particular case, `--encrypt` was used a second time rather than
`--decipher`.  Using `--decipher` after `--reversible` will give similar
results.  Likewise, a default `--reversible` will not decode a ciphertext
generated with `--encrypt`.

```
><)> ./cipher.py -k Dvorak --encrypt --include original.swp
…fa, uv ylwh, tvp+rxzik
…is, in fact, GNU+Linux
----------------!------
…bz, js puhf, wrj+suvpp
…ys, ec bzmg, rss+tklfj
…gl, yt xkrd, hni+nfnui
…mq, pl intt, gcz+ldokx
…ho, iz upvm, nte+vprye
…dz, kr dsgb, vwl+ciaxu
…is, xw kacw, clk+wysdy
…xl, jn fvnc, mzy+zbqbp
----------------!------
…is, in fact, GNU+Linux
…fa, uv ylwh, tvp+rxzik
```

Note how the only missing letter here is a single instance of `u`.

#### Getting `--encrypt` and `--decipher` backwards

```
><)> echo "Hello (good 2B back)!" | ./cipher.py --decipher --only-one - | ./cipher.py --encrypt -
jdooibaixvyxsl
hellogoodbback
----------!---
irikknxmwcndwo
mepimypkaguzeq
uflplhsjsrtwci
hcklofoudfbeqa
nsikutloqbjazz
kwpijvzlcegqxp
yxlpkrwmztmsdk
ivklmgqkedhcao
----------!---
hellogoodbback
jdooibaixvyxsl
```

Again, only a single `b` is missing.

## Ideas for Extension

These are ideas that you, the user, are free to run with.  I currently lack the
interest to see these projects through to completion, but they would be
valuable additions towards the use of this tool for cracking these ciphers.

* Automate using a dictionary to find words in a ciphered text
* An interactive tool to use a dictionary to find words from ciphertext
* Implement unambiguous reversal of `--fixed` ciphertexts

## Running Tests

`./test.py --help` will tell you how to test with custom phrases
