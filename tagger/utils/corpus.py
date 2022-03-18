# -*- coding: utf-8 -*-

from collections import namedtuple
from operator import itemgetter

Sentence = namedtuple(typename='Sentence',
                      field_names=['ID', 'FORM', 'LEMMA', 'UPOS',
                                   'POS', 'FEATS', 'HEAD', 'DEPREL',
                                   'PHEAD', 'PDEPREL'],
                      defaults=[None]*10)

class RawCorpus(object):
    ROOT = '<ROOT>'
    PAD = '<PAD>'

    def __init__(self, sentences):
        super(RawCorpus, self).__init__()
        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)


    def __getitem__(self, index):
        return self.sentences[index]

    @property
    def words(self):
        return [[self.ROOT] + list(sentence.FORM) for sentence in self]

    @property
    def lemmas(self):
        return [[self.ROOT] + list(sentence.LEMMA) for sentence in self]

    # for compatibility
    @property
    def tags(self):
        return [[self.ROOT] + list(sentence.UPOS) for sentence in self]

    @property
    def feats(self):
        return [[self.ROOT] + list(sentence.FEATS) for sentence in self]

    
    @property
    def heads(self):
        return [[0] + list(map(int, sentence.HEAD)) for sentence in self]

    @property
    def rels(self):
        return [[self.ROOT] + list(sentence.DEPREL) for sentence in self]

    @classmethod
    def load(cls, fname):
        start, sentences = 0, []
        with open(fname, 'r') as f:
            lines = [line for line in f]
        for line in lines:
            line = line.strip().split()
            num_tokens = len(line)
            sentence = Sentence(None,
                                line,
                                [cls.PAD] * num_tokens,
                                [cls.PAD] * num_tokens,
                                [cls.PAD] * num_tokens,
                                [cls.PAD] * num_tokens,
                                [0] * num_tokens,
                                [cls.PAD] * num_tokens,
                                [cls.PAD] * num_tokens,
                                [cls.PAD] * num_tokens)
            sentences.append(sentence)
        corpus = cls(sentences)
        return corpus

    def save(self, fname):
        with open(fname, 'w') as f:
            f.write(f"{self}\n")


class Corpus(object):
    ROOT = '<ROOT>'

    def __init__(self, sentences):
        super(Corpus, self).__init__()
        self.sentences = sentences

    def __len__(self):
        return len(self.sentences)

    def __repr__(self):
        return '\n'.join(
            '\n'.join('\t'.join(map(str, i))
                      for i in zip(*(f for f in sentence if f))) + '\n'
            for sentence in self
        )

    def __getitem__(self, index):
        return self.sentences[index]

    @property
    def words(self):
        return [[self.ROOT] + list(sentence.FORM) for sentence in self]

    @property
    def lemmas(self):
        return [[self.ROOT] + list(sentence.LEMMA) for sentence in self]

    @property
    def tags(self):
        return [[self.ROOT] + list(sentence.UPOS) for sentence in self]

    @property
    def feats(self):
        return [[self.ROOT] + list(sentence.FEATS) for sentence in self]

    @property
    def heads(self):
        return [[0] + list(map(int, sentence.HEAD)) for sentence in self]

    @property
    def rels(self):
        return [[self.ROOT] + list(sentence.DEPREL) for sentence in self]
    
    @heads.setter
    def heads(self, sequences):
        self.sentences = [sentence._replace(HEAD=sequence)
                          for sentence, sequence in zip(self, sequences)]

    @rels.setter
    def rels(self, sequences):
        self.sentences = [sentence._replace(DEPREL=sequence)
                          for sentence, sequence in zip(self, sequences)]

    @tags.setter
    def tags(self, sequences):
        self.sentences = [sentence._replace(UPOS=sequence)
                          for sentence, sequence in zip(self, sequences)]


    @classmethod
    def load(cls, fname):
        start, sentences = 0, []
        with open(fname, 'r') as f:
            lines = [line for line in f if not line.startswith("#")]
        for i, line in enumerate(lines):
            if len(line) <= 1:
                entries = [l.split("\t") for l in lines[start:i]]
                good_entries = []
                for entry in entries:
                    try:
                        int(entry[0])
                        entry[-1] = entry[-1].strip()
                        entry[7] = entry[7].split(":")[0]
                        good_entries.append(entry)    
                    except:
                        pass
                        
                sentence = Sentence(*zip(*good_entries))
                
                sentences.append(sentence)
                start = i + 1
       
        corpus = cls(sentences)

        return corpus

    def save(self, fname):
        with open(fname, 'w') as f:
            f.write(f"{self}\n")

    
