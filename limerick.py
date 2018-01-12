#!/usr/bin/env python
from collections import defaultdict
import argparse
import sys
import codecs
if sys.version_info[0] == 2:
  from itertools import izip
else:
  izip = zip
from collections import defaultdict as dd
import re
import os.path
import gzip
import tempfile
import shutil
import atexit

# Use word_tokenize to split raw text into words
from string import punctuation

import nltk
from nltk.tokenize import word_tokenize

scriptdir = os.path.dirname(os.path.abspath(__file__))

reader = codecs.getreader('utf8')
writer = codecs.getwriter('utf8')

def prepfile(fh, code):
  if type(fh) is str:
    fh = open(fh, code)
  ret = gzip.open(fh.name, code if code.endswith("t") else code+"t") if fh.name.endswith(".gz") else fh
  if sys.version_info[0] == 2:
    if code.startswith('r'):
      ret = reader(fh)
    elif code.startswith('w'):
      ret = writer(fh)
    else:
      sys.stderr.write("I didn't understand code "+code+"\n")
      sys.exit(1)
  return ret

def addonoffarg(parser, arg, dest=None, default=True, help="TODO"):
  ''' add the switches --arg and --no-arg that set parser.arg to true/false, respectively'''
  group = parser.add_mutually_exclusive_group()
  dest = arg if dest is None else dest
  group.add_argument('--%s' % arg, dest=dest, action='store_true', default=default, help=help)
  group.add_argument('--no-%s' % arg, dest=dest, action='store_false', default=default, help="See --%s" % arg)



class LimerickDetector:

    def __init__(self):
        """
        Initializes the object to have a pronunciation dictionary available
        """
        self._pronunciations = nltk.corpus.cmudict.dict()


    def num_syllables(self, word):
        """
        Returns the number of syllables in a word.  If there's more than one
        pronunciation, take the shorter one.  If there is no entry in the
        dictionary, return 1.
        """
        if not word.lower() in self._pronunciations:
            return 1
    
        return min([len(list(y for y in x if y[-1].isdigit())) for x in self._pronunciations[word.lower()]])
        # TODO: provide an implementation!

        

    def rhymes(self, a, b):
        """
        Returns True if two words (represented as lower-case strings) rhyme,
        False otherwise.
        """
        word1=self._pronunciations[a.lower()]
        word2=self._pronunciations[b.lower()]
        rhyme1=[]
        rhyme2=[]
        for index1,w1 in enumerate(word1):
            for index2,syllable in enumerate(w1):
                if syllable[-1].isdigit()==True:
                    rhyme1.append(w1[index2:])
                    break

        for index3,w2 in enumerate(word2):
            for index4,syllable in enumerate(w2):
                if syllable[-1].isdigit()==True:
                    rhyme2.append(w2[index4:])
                    break
        
        x=False
        y=False
        z=False
        
        for r1 in rhyme1:
            for r2 in rhyme2:
                r1="".join(r1)
                r2="".join(r2)
                if(x or y or z):
                    break
                else:
                    if len(r1)<len(r2):
                        
                        x=True if r1 in r2[-len(r1):] else False
                        if x is True: break
                    elif len(r2)<len(r1):
                        
                        y=True if r2 in r1[-len(r2):] else False
                        if y is True: break
                    elif len(r1)==len(r2):

                        z=True if r1 in r2 else False
                        if z is True: break
        
        if(x or y or z):
            return True
        else:
            return False


        # TODO: provide an implementation!

        

    def is_limerick(self, text):
        """
        Takes text where lines are separated by newline characters.  Returns
        True if the text is a limerick, False otherwise.

        A limerick is defined as a poem with the form AABBA, where the A lines
        rhyme with each other, the B lines rhyme with each other, and the A lines do not
        rhyme with the B lines.


        Additionally, the following syllable constraints should be observed:
          * No two A lines should differ in their number of syllables by more than two.
          * The B lines should differ in their number of syllables by no more than two.
          * Each of the B lines should have fewer syllables than each of the A lines.
          * No line should have fewer than 4 syllables

        (English professors may disagree with this definition, but that's what
        we're using here.)"""
    
        lines=text.split("\n")
        lines=[''.join(x for x in line if x.isalpha() or x.isspace()).strip() for line in lines if line.strip()]



        token_words=[]

        words=[]

        for line in lines:
            if str(line)==" " or line==[]:
                continue
            else:
                words.append(line)

        count_lines=len(words)

        if(count_lines==5):
            for line in words:
                token_words.append(word_tokenize(line))

            no_syllables=defaultdict(list)
            for i in xrange(0,len(token_words)):
                for word in token_words[i]:
                    no_syllables[i].append(self.num_syllables(word))
            a1=sum(no_syllables[0])
            a2=sum(no_syllables[1])
            b1=sum(no_syllables[2])
            b2=sum(no_syllables[3])
            a3=sum(no_syllables[4])
            if(abs(a1-a2)<=2 and abs(a1-a3)<=2 and abs(a2-a3)<=2):
                if(abs(b1-b2)<=2 and a1>=4 and a2>=4 and a3>=4 and b1>=4 and b2>=4):
                    if(self.rhymes(token_words[0][-1],token_words[1][-1]) and self.rhymes(token_words[0][-1],token_words[4][-1]) and self.rhymes(token_words[1][-1],token_words[4][-1])):

                        if(self.rhymes(token_words[2][-1],token_words[3][-1])):

                            if(self.rhymes(token_words[0][-1],token_words[2][-1])!=True):
                                return True
                            else:
                                return False
                        else:
                            return False
                    else:
                        return False
                else:
                    return False
            else:
                return False

        elif(count_lines<5 or count_lines>5):
            return False



        
        # TODO: provide an implementation!
        


# The code below should not need to be modified
def main():
    parser = argparse.ArgumentParser(description="limerick detector. Given a file containing a poem, indicate whether that poem is a limerick or not",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    addonoffarg(parser, 'debug', help="debug mode", default=False)
    parser.add_argument("--infile", "-i", nargs='?', type=argparse.FileType('r'), default=sys.stdin, help="input file")
    parser.add_argument("--outfile", "-o", nargs='?', type=argparse.FileType('w'), default=sys.stdout, help="output file")




    try:
        args = parser.parse_args()
    except IOError as msg:
        parser.error(str(msg))

    infile = prepfile(args.infile, 'r')
    outfile = prepfile(args.outfile, 'w')

    ld = LimerickDetector()
    lines = ''.join(infile.readlines())
    outfile.write("{}\n-----------\n{}\n".format(lines.strip(), ld.is_limerick(lines)))

if __name__ == '__main__':
      main()

