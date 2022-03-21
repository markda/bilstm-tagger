# -*- coding: utf-8 -*-

import os
from datetime import datetime, timedelta, date
from tagger import Tagger, Model
from tagger.metric import Metric
from tagger.utils import Corpus, Embedding, Vocab
from tagger.utils.data import TextDataset, batchify
import torch
from torch.optim import Adam
from torch.optim.lr_scheduler import ExponentialLR
import csv

class Train(object):

    def add_subparser(self, name, parser):
        subparser = parser.add_parser(
            name, help='Train a model.'
        )
        subparser.add_argument('--buckets', default=64, type=int,
                               help='max num of buckets to use')
        subparser.add_argument('--punct', action='store_false', default=True,
                               help='whether to include punctuation')
        subparser.add_argument('--ftrain', default='data/ptb/train.conllx',
                               help='path to train file')
        subparser.add_argument('--fdev', default='data/ptb/dev.conllx',
                               help='path to dev file')
        subparser.add_argument('--fembed', default=False,
                               help='path to pretrained embeddings')
        subparser.add_argument('--n_char_embed', default=100, type=int,
                               help='char embedding size')
        subparser.add_argument('--unk', default='unk',
                               help='unk token in pretrained embeddings')
        subparser.add_argument('--load_model', default=None)
        subparser.add_argument('--load_vocab', default=None)
        subparser.add_argument("--n_lstm_nodes", default=None, type=int)
        subparser.add_argument("--n_lstm_layers", default=None, type=int)
        
        
        return subparser

    def __call__(self, config):
        #if config.lstm_nodes is not None:
        #    
        #if config.lstm_layers is not None:
        #    
        config.n_lstm_hidden = config.n_lstm_nodes
        config.n_lstm_layers = config.n_lstm_layers
        print("Preprocess the data")
        train = Corpus.load(config.ftrain)
        dev = Corpus.load(config.fdev)

        print("Generating vocab.")
        vocab= Vocab.from_corpus(corpus=train, min_freq=5)
        if config.fembed:
            print("Loading embeddings.")
            vocab.read_embeddings(Embedding.load(config.fembed, config.unk, config.n_embed))
        else:
            print("Randomly initiliasing embeddings.")
            vocab.randomly_initialise_embeddings(config.n_embed)
        torch.save(vocab, config.vocab)

        config.update({
            'n_words': vocab.n_words,
            'n_tags': vocab.n_tags,
            'n_chars': vocab.n_chars,
            'pad_index': vocab.pad_index,
            'unk_index': vocab.unk_index
        })
        print(vocab)
       
        print("Load the dataset")
        trainset = TextDataset(vocab.numericalize(train))
        devset = TextDataset(vocab.numericalize(dev))

        # set the data loaders
        train_loader = batchify(dataset=trainset,
                                batch_size=config.batch_size,
                                shuffle=True)
        dev_loader = batchify(dataset=devset,
                              batch_size=config.batch_size)
        print(f"{'train:':6} {len(trainset):5} sentences in total, "
              f"{len(train_loader):3} batches provided")
        print(f"{'dev:':6} {len(devset):5} sentences in total, "
              f"{len(dev_loader):3} batches provided")

        print("Creating model")
    
        tagger = Tagger(config, vocab.embeddings)
       
        if torch.cuda.is_available():
            tagger = tagger.cuda()
        print(f"{tagger}\n")

        model = Model(vocab, tagger)

        total_time = timedelta()
        best_e, best_metric = 1, -99.99
        best_train_metric = -99.99
        model.optimizer = Adam(model.tagger.parameters(),
                               config.lr,
                               (config.beta_1, config.beta_2),
                               config.epsilon)
        model.scheduler = ExponentialLR(model.optimizer,
                                        config.decay ** (1 / config.steps))
        epochs_since_improvement = 0

        total_params = sum(p.numel() for p in model.tagger.parameters())
        print ("Total number of parameters:", total_params,"\n")
        for epoch in range(1, config.epochs + 1):
            start = datetime.now()
            # train one epoch and update the parameters
            model.train(train_loader)

            print(f"Epoch {epoch} / {config.epochs}:")
            loss, train_metric = model.evaluate(train_loader, config.punct)
            print(f"{'train:':6} Loss: {loss:.4f} \t Acc: {train_metric:.2f}")
            loss, dev_metric = model.evaluate(dev_loader, config.punct)
            print(f"{'dev:':6} Loss: {loss:.4f} \t Acc: {dev_metric:.2f}")
            
            t = datetime.now() - start
            # save the model if it is the best so far
            if dev_metric > best_metric:
                best_e, best_metric = epoch, dev_metric
                best_train_metric = train_metric
                model.tagger.save(config.model)
                print(f"{t}s elapsed (saved)\n")
                epochs_since_improvement = 0
            else:
                epochs_since_improvement += 1
                print(f"{t}s elapsed\n")
            if epochs_since_improvement >= config.patience:
                print("¡Lo bailado nadie te lo quita!\n")
                break
            total_time += t
        

        
        print(f"max score of dev is {best_metric:.2f} at epoch {best_e}")
        print(f"average time of each epoch is {total_time / epoch}s")
        print(f"{total_time}s elapsed")
                                      
