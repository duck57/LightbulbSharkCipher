# The Shark Cipher

## About the Cipher

The operation of this cipher is outlined in Letter #111 from the First Eric
Sanderson (presented on pages 73--76 of _The Raw Shark Texts_ by Steven Hall).
~~A major implication of these instructions is that the process to encode a
message is identical to the process used to decode a ciphertext: the difference
lies in how you go from your list of possibilities of each character to the
final output.~~

Using the cipher in the manner strictly outlined in the book is not, in fact,
reversible.  

## Using this program

### System Requirements

Python 3.8+ with Click installed (see `requirements.txt`)

### Command Options

Run `./cipher.py --help` to read about all the various options for output.

### Decoding

TK show example of ciphered text containing the original message

The example input phrase is `What you are refering to as Linux`.

## Ideas for Extension

These are ideas that you, the user, are free to run with.  I currently lack the
interest to see these projects through to completion, but they would be valuable
additions towards the use of this tool for cracking these ciphers.

* Automate using a dictionary to find words in a ciphered text
* An interactive tool to use a dictionary to find words from ciphertext

## Running Tests

`./test.py --help` will tell you how to test with custom phrases
