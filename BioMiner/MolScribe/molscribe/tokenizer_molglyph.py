import os
import re
import json
import random
import numpy as np
from SmilesPE.pretokenizer import atomwise_tokenizer

PAD = '<pad>'
SOS = '<sos>'
EOS = '<eos>'
UNK = '<unk>'
MASK = '<mask>'
SEP = '<sep>'
atom_start = '<a>'
atom_end = '</a>'
circ_start = '<c>'
circ_end = '</c>'
ring_start = '<r>'
ring_end = '</r>'
dummy = '<dum>'

PAD_ID = 0
SOS_ID = 1
EOS_ID = 2
UNK_ID = 3
MASK_ID = 4
SEP_ID = 5
atom_start_ID = 6
atom_end_ID = 7
circ_start_ID = 8
circ_end_ID = 9
ring_start_ID = 10
ring_end_ID = 11
dummy_ID = 12

class Tokenizer(object):

    def __init__(self, path=None):
        self.stoi = {}
        self.itos = {}
        if path:
            self.load(path)

    def __len__(self):
        return len(self.stoi)

    @property
    def output_constraint(self):
        return False

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.stoi, f)

    def load(self, path):
        with open(path) as f:
            self.stoi = json.load(f)
        self.itos = {item[1]: item[0] for item in self.stoi.items()}

    def fit_on_texts(self, texts):
        vocab = set()
        for text in texts:
            vocab.update(text.split(' '))
        vocab = [PAD, SOS, EOS, UNK] + list(vocab)
        for i, s in enumerate(vocab):
            self.stoi[s] = i
        self.itos = {item[1]: item[0] for item in self.stoi.items()}
        assert self.stoi[PAD] == PAD_ID
        assert self.stoi[SOS] == SOS_ID
        assert self.stoi[EOS] == EOS_ID
        assert self.stoi[UNK] == UNK_ID

    def text_to_sequence(self, text, tokenized=True):
        sequence = []
        sequence.append(self.stoi['<sos>'])
        if tokenized:
            tokens = text.split(' ')
        else:
            tokens = atomwise_tokenizer(text)
        for s in tokens:
            if s not in self.stoi:
                s = '<unk>'
            sequence.append(self.stoi[s])
        sequence.append(self.stoi['<eos>'])
        return sequence

    def texts_to_sequences(self, texts):
        sequences = []
        for text in texts:
            sequence = self.text_to_sequence(text)
            sequences.append(sequence)
        return sequences

    def sequence_to_text(self, sequence):
        return ''.join(list(map(lambda i: self.itos[i], sequence)))

    def sequences_to_texts(self, sequences):
        texts = []
        for sequence in sequences:
            text = self.sequence_to_text(sequence)
            texts.append(text)
        return texts

    def predict_caption(self, sequence):
        caption = ''
        for i in sequence:
            if i == self.stoi['<eos>'] or i == self.stoi['<pad>']:
                break
            caption += self.itos[i]
        return caption

    def predict_captions(self, sequences):
        captions = []
        for sequence in sequences:
            caption = self.predict_caption(sequence)
            captions.append(caption)
        return captions

    def sequence_to_smiles(self, sequence):
        return {'smiles': self.predict_caption(sequence)}
    
class MolparserCaptionTokenizer(Tokenizer):

    def __init__(self, path):
        super().__init__(path)
        self.special_tokens = [PAD, SOS, EOS, UNK, MASK, SEP, atom_start, atom_end, circ_start, circ_end, ring_start, ring_end, dummy]

    def is_symbol(self, s):
        return len(self.special_tokens) <= s or s == UNK_ID

    def is_atom(self, id):
        if self.is_symbol(id):
            return self.is_atom_token(self.itos[id])
        return False

    def is_atom_token(self, token):
        return token.isalpha() or token.startswith("[") or token == '*' or token == UNK
    
    def sequence_to_smiles(self, sequence):
        smiles = ''
        i = 0
        while i < len(sequence):
            label = sequence[i]
            if label == EOS_ID or label == PAD_ID:
                break
            smiles += self.itos[label]
            i += 1

        results = {'smiles': smiles, 'symbols': None, 'indices': None}
        return results  
    
def get_molglyph_tokenizer(args):
    tokenizer = {}
    for format_ in args.formats:
        if format_ == 'molparser_caption':
            if args.vocab_file is None:
                args.vocab_file = os.path.join(os.path.dirname(__file__), 'vocab/vocab_molparser.json')
            tokenizer["molparser_caption"] = MolparserCaptionTokenizer(args.vocab_file)

    return tokenizer
