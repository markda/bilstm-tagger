# -*- coding: utf-8 -*-

from collections import Counter

import regex
import torch


class Vocab(object):
    PAD = '<PAD>'
    UNK = '<UNK>'

    def __init__(self, words, tags, chars, rels):
        self.pad_index = 0
        self.unk_index = 1

        self.words = [self.PAD, self.UNK] + sorted(words)
        self.tags = [self.PAD, self.UNK] + sorted(tags)
        self.chars = [self.PAD, self.UNK] + sorted(chars)
        self.rels = sorted(rels)

        self.word_dict = {word: i for i, word in enumerate(self.words)}
        self.tag_dict = {tag: i for i, tag in enumerate(self.tags)}
        self.char_dict = {char: i for i, char in enumerate(self.chars)}
        self.rel_dict = {rel: i for i, rel in enumerate(self.rels)}

        # ids of punctuation that appear in words
        self.puncts = sorted(i for word, i in self.word_dict.items()
                             if regex.match(r'\p{P}+$', word))

        self.n_words = len(self.words)
        self.n_tags = len(self.tags)
        self.n_chars = len(self.chars)
        self.n_rels = len(self.rels)
        self.n_train_words = self.n_words

    def __repr__(self):
        info = f"{self.__class__.__name__}: "
        info += f"{self.n_words} words, "
        info += f"{self.n_tags} tags, "
        info += f"{self.n_chars} chars, "
        info += f"{self.n_rels} rels"

        return info

    def word2id(self, sequence):
        return torch.tensor([self.word_dict.get(word.lower(), self.unk_index)
                             for word in sequence])

    def char2id(self, sequence, max_length=20):
        char_ids = torch.zeros(len(sequence), max_length, dtype=torch.long)
        for i, word in enumerate(sequence):
            ids = torch.tensor([self.char_dict.get(c, self.unk_index)
                                for c in word[:max_length]])
            char_ids[i, :len(ids)] = ids

        return char_ids

    def rel2id(self, sequence):
        return torch.tensor([self.rel_dict.get(rel, 0)
                             for rel in sequence])

    def id2rel(self, ids):
        return [self.rels[i] for i in ids]

    def read_embeddings(self, embed, smooth=True):
        # if the UNK token has existed in the pretrained,
        # then use it to replace the one in the vocab
        if embed.unk:
            self.UNK = embed.unk

        self.extend(embed.tokens)
        self.embeddings = torch.zeros(self.n_words, embed.dim)

        for i, word in enumerate(self.words):
            if word in embed:
                self.embeddings[i] = embed[word]
        if smooth:
            self.embeddings /= torch.std(self.embeddings)

    def extend(self, words):
        self.words += sorted(set(words).difference(self.word_dict))
        self.chars += sorted(set(''.join(words)).difference(self.char_dict))
        self.word_dict = {w: i for i, w in enumerate(self.words)}
        self.char_dict = {c: i for i, c in enumerate(self.chars)}
        self.puncts = sorted(i for word, i in self.word_dict.items()
                             if regex.match(r'\p{P}+$', word))
        self.n_words = len(self.words)
        self.n_chars = len(self.chars)

    def numericalize(self, corpus, training=True):
        words = [self.word2id(seq) for seq in corpus.words]
        tags = [self.tag2id(seq) for seq in corpus.tags]
        chars = [self.char2id(seq) for seq in corpus.words]
        if not training:
            return words, tags, chars
        arcs = [torch.tensor(seq) for seq in corpus.heads]
        rels = [self.rel2id(seq) for seq in corpus.rels]

        return words, tags, chars, arcs, rels

    @classmethod
    def from_corpus(cls, corpus, min_freq=1):
        words = Counter(word.lower() for seq in corpus.words for word in seq)
        words = list(word for word, freq in words.items() if freq >= min_freq)
        tags = list({tag for seq in corpus.tags for tag in seq})
        chars = list({char for seq in corpus.words for char in ''.join(seq)})
        rels = list({rel for seq in corpus.rels for rel in seq})
        vocab = cls(words, chars, rels)

        return vocab
