#
# To instantiate a chunker:
#
# x = chunker.Chunker()
#
# To Chunk:
#
# x.chunk(string)
#
# Example:
#
# import chunker
# chk = chunker.Chunker()
# chunk_tree = chk.chunk("Who directed \"The Big Lebowski\"?")

import nltk
import pickle
from os import path
import string

class Chunker:

    def __init__(self, verbose=False, test = False):

        if verbose:
            print "#Initializing chunker:"
        
        # Define regular expressions for punctuation tags
        tagged_punc = [ (r'\"', ':'), (r'\?', 'QM'),(r'\.', 'EOS') ]
        
        
        
        # Load the tagged training sentences.
        if not test:
            f = open( path.join(path.dirname(__file__),'training_sentences.bin'), 'rb' )
            train_sents = pickle.load(f)
            if verbose:
                print " Loading POS tagged training sentences:"
                print f
        elif test:
            f = open( path.join(path.dirname(__file__),'test_sentences'), 'r' )
            train_sents = pickle.load(f)
        
        
        # Define the tagger.
        
        if verbose:
            print " Loading maxent_treebank_pos_tagger."
        
        _POS_TAGGER = 'taggers/maxent_treebank_pos_tagger/english.pickle'
        t1 = nltk.data.load(_POS_TAGGER)
        if verbose:
            print " Training custom Unigram Tagger."
        t2 = nltk.UnigramTagger( train_sents, backoff=t1 )
        
        if verbose:
            print " Instantiating tagger object."
        
        self.tagger = nltk.RegexpTagger( tagged_punc, backoff=t2 )
        
        # Define a chunking grammar.
        chunk_grammar = r"""
        B-QUESTION: {<WDT|WP|WRB><DT|RB.*|JJ|GNRE>*<MD|VB.*|KW_.*>}
            {<WRB>}
        COMMAND: {^(<MD><PRP>)?(<RB>)*<VB|VBP>}
            {^<PRP><VB|VBP><TO>}
            {<RB><VBP|VB>}
        TRUE_FALSE: {^<VBD|VBZ>}
        TITLE: {<:><[^:]*>*<:>}
        PERSON: {<NNP[S]?>+}
        NP: {<PRP\$>?<JJ>*<NN|NNS>(<POS>?<JJ>*<NN|NNS>)*}        
        PP: { <IN><NP> }
        """
        #ACTOR_IN_MOVIE: {<PERSON><.*>*<IN><TITLE>}
        #S: {<CC><.*>*}
        #B-QUESTION: {^<[W].*|VBD|VBN|VBP|VBZ>}
        if verbose:
            print " Instantiating RegexpParser object."
        
        # Define a regular expression chunker
        self.cp = nltk.RegexpParser(chunk_grammar)
        
        if verbose:
            print "Chunker Initialized.#"
    
    def chunk(self, sentence):
        if "." in sentence:
            sentence = string.replace(sentence,"."," . ")
        tokd = nltk.word_tokenize(sentence)
        tagged = self.tagger.tag(tokd)
        if ('like', 'IN') in tagged:
           i = tagged.index(('like', 'IN'))
           if i==0 or tagged[i-1]!=('do','VBP'):
               tagged.insert(i,('like','KW_SIMILAR'))
               tagged.remove(('like', 'IN'))
        #print tagged
        chunked = self.cp.parse(tagged)
        return chunked

if __name__ == '__main__':
    with open(path.join(path.dirname(__file__), "chunkerpickler.bin"),'rb') as pickled_file:
        chk = pickle.load(pickled_file)
#    chk = Chunker(False, True)
    result = chk.chunk("""I want to see some super hero movie""")
    print result
    result.draw()

"""
What are some movies made by Quentin Tarantino but without Uma Thurman?
I like movies like "God Father" or "The load of the rings".
I don't like Tom Cruise but I think "Magnolia" is good. Please show me some movies like that.
Which movie by Tom Hanks earns the most?
Do you know what the most popular movie was in 2004?
Where can I watch avatar? Would you like to show theaters around you?
In what year was "Jumanji" released?
Do you know when "Titanic" came out?
Restart. I like Tom Hanks, but I don't like action movies. I want twenty two
has he won any awards?
Could you tell me about "Titanic"?
I want to see some super hero movie?
Who starred Marty in "Back to the Future"?
How about a romantic movie with Nicole Kidman?
List the highly rated movies that BensTiller was in.
Can you suggest me some good action movies?
I don't like Tom Cruise but I think "Magnolia" is good. Please show me some movies like that.
Is "Beauty and the Beast" animated?
How many movies has Walt Disney directed?
Are there other movies that are similar to "Inception"?
"""
