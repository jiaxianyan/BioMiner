import argparse
import json
import torch
from tqdm import tqdm
import os 
import warnings 
from collections import defaultdict
warnings.filterwarnings('ignore')
import pandas as pd
from rdkit import Chem, RDLogger
from rdkit.Chem.rdchem import Mol
from rdkit.Chem.Draw import rdMolDraw2D
from typing import Optional, List, Tuple, Union, Dict
import re
import logging
from pathlib import Path
from dataclasses import dataclass
from functools import reduce
from enum import Enum, unique

# python predict.py --model_path ckpts/swin_base_char_aux_1m680k.pth --image_path assets/example.png
logger = logging.getLogger(__name__)

# Load group abbreviations.
@dataclass(frozen=True)
class Abbreviation:
    name: str
    smi: str
    num_atoms: int  # exclude hydrogen
    symbol: str  # used for target
    label: str
    labelW: str
    
    def __str__(self) -> str:
        return f'{self.symbol} {self.smi} {self.label} {self.labelW}'


_abbrev_df = pd.read_csv(
    str(Path(__file__).parent/'abbrevs.csv'), header=0, index_col=False
)
_abbrev_smi = dict()
_abbrev_dict = defaultdict(list)
for row in _abbrev_df.itertuples():
    _abbrev_dict[row.name].append(Abbreviation(
        name=row.name, smi=row.smiles, num_atoms=int(row.atoms),
        symbol=row.symbol, label=row.label, labelW=row.labelW
    ))
    _abbrev_smi[row.symbol] = row.smiles
    
abbr_to_smiles = {}

for smi, sym in zip(_abbrev_df['smiles'], _abbrev_df['symbol']):
    abbr_to_smiles[sym] = smi

def get_abbrev_smi() -> Dict[str, str]:
    return _abbrev_smi

def to_smiles(mol: Chem.rdchem.Mol, canonical: bool = False) -> str:
    return Chem.MolToSmiles(mol, rootedAtAtom=0, canonical=canonical)

def get_mol(smi: str) -> Chem.rdchem.Mol:
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        raise ValueError(f'Invalid SMILES: {smi}')
    return mol

def merge_group(tgt_mol: Chem.rdchem.RWMol, src: str, attach_idx: int) -> None:
    """Merge a group of abbreviation into target molecule in place."""
    dummy_atom = tgt_mol.GetAtomWithIdx(attach_idx)
    assert dummy_atom.GetSymbol() == '*', 'Non-dummy attachment point'
    src_mol = get_mol(src)
    
    # Find index of the only neighbor of dummy attachment.
    neighbors = dummy_atom.GetNeighbors()
    assert len(neighbors) == 1, 'Attachment point must have exactly one neighbor'
    nb_idx = neighbors[0].GetIdx()  # real attachment point
    
    # Ensure single bond type.
    conn_bond = tgt_mol.GetBondBetweenAtoms(attach_idx, nb_idx)
    assert conn_bond.GetBondType() == Chem.BondType.SINGLE, (
        'Attachment point must link to single bond'
    )
    
    # Add atoms from source to target.
    # NOTE Keep track of the mapping between atom indices, as well as index of
    # the first atom in group in target molecule.
    idx_map = {}  # key: `g_mol` atom index, value: target mol atom index
    for atom in src_mol.GetAtoms():
        i = tgt_mol.AddAtom(atom)
        idx_map[atom.GetIdx()] = i
    # Add bonds from source to target.
    for bond in src_mol.GetBonds():
        begin_idx = bond.GetBeginAtomIdx()
        end_idx = bond.GetEndAtomIdx()
        j, k = idx_map[begin_idx], idx_map[end_idx]
        tgt_mol.AddBond(j, k, bond.GetBondType())
    # Attach first atom of source molecule to target molecule.
    # NOTE We cannot delete dummy atom now, as atom order must be preserved, instead
    # we delete them outside this funciton.
    tgt_mol.RemoveBond(attach_idx, nb_idx)  # must be done first
    tgt_mol.AddBond(nb_idx, idx_map[0], Chem.BondType.SINGLE)

def is_single_bond(bond: Chem.rdchem.Bond) -> bool:
    """Helper function for detecting single bonds."""
    return bond.GetBondType() == Chem.rdchem.BondType.SINGLE

class Index(int):
    def __new__(cls, value: int, **kwds):
        assert isinstance(value, int) and value >= 0
        return super().__new__(cls, value)

@unique
class TextType(Enum):
    SYMBOL = 'symbol'
    SCRIPT = 'script'
    MULTIPLE = 'multiple'
    PRIME = 'prime'

class AtomIndex(Index):
    key: int = 1
    
    def __hash__(self):
        return hash(('atom', int(self)))
    
    def __eq__(self, other):
        if isinstance(other, AtomIndex):
            return hash(self) == hash(other)
        return False


class RingIndex(Index):
    def __init__(self, value: int, virtual: bool = False) -> None:
        self._virtual = virtual
        self._key = 2_000_000 if self._virtual else 1_000_000
        
    def __hash__(self):
        return hash(('ring', int(self), self._virtual))
    
    def __eq__(self, other):
        if isinstance(other, RingIndex):
            return hash(self) == hash(other)
        return False
    
    @property
    def virtual(self) -> bool:
        return self._virtual
    
    @property
    def key(self) -> bool:
        return self._key

LONG_CHAR_ELEMENTS = (
    'Cl', 'Br', 'Si', 'Na', 'Al', 'Ca', 'Sn', 'As', 'Hg',
    'Fe', 'Zn', 'Cr', 'Se', 'Gd', 'Au', 'Li'
)
VISUALIZE_CFG = {
    'padding': 0.1,
    'additionalAtomLabelPadding': 0.05, 
    'fixedFontSize': 12,
    'bondLineWidth': 1,
    'multipleBondOffset': 0.1,
    'dummiesAreAttachments': False,
    'addAtomIndices': False,
    'singleColourWedgeBonds': True,
    'legendFontSize': 9,
}

class Tokens:
    """A class of sepcial token definitions."""
    atom_start = '<a>'
    atom_end = '</a>'
    circ_start = '<c>'
    circ_end = '</c>'
    ring_start = '<r>'
    ring_end = '</r>'
    dummy = '<dum>'
    separator = '<sep>'

    
class Patterns:
    """A class of molecular expression patterns."""
    long_char_elements_pattern = re.compile(rf'{"|".join(LONG_CHAR_ELEMENTS) + "|."}') 
    grp_content = re.compile(
        rf'(?P<{TextType.SYMBOL.value}>[A-Za-z0-9]*)' +
        rf'(?P<{TextType.SCRIPT.value}>(\[\S+\])?)' +
        rf'(?P<{TextType.PRIME.value}>[\'\"]?)' +
        rf'(?P<{TextType.MULTIPLE.value}>(\?([a-z]|\d{1}|\d-\d)$)?)'  # $ for matching string ending
    )
    grp_pattern = re.compile(
        rf'({Tokens.atom_start}|{Tokens.circ_start}|{Tokens.ring_start}|{Tokens.ring_start}{Tokens.circ_start})' +
        rf'(\d+:\S+?)' +
        rf'({Tokens.atom_end}|{Tokens.circ_end}|{Tokens.ring_end})'
    )
    trail_pattern = re.compile(r'(?P<groups>([^|]*)?)(?P<extension>(\|\S+\|)?$)')


@dataclass
class GroupDesc:
    id: Index
    symbol: Optional[str] = None
    script: Optional[str] = None
    prime: Optional[str] = None
    multiple: Optional[str] = None
    is_circle: bool = False
    is_dummy: bool = False
    
    @property
    def is_abbrev(self) -> bool:
        """Determine if the group describes abbreviation."""
        return (
            isinstance(self.id, AtomIndex)
            and (not self.is_dummy)
            and (not self.is_circle)
            and self.symbol in get_abbrev_smi()
            and self.symbol != 'Ar'  # `Ar` might be a variable aromatic ring
            and self.script is None
            and self.prime is None
            and self.multiple is None
        )
        
    def __str__(self) -> str:
        if self.is_dummy:
            return '<dum>'
        expr = ''
        if self.is_circle:
            expr = 'c'
        if self.symbol is not None:
            expr += self.symbol
        if self.script is not None:
            expr = expr + '[' + self.script + ']'
        if self.prime is not None:
            expr += self.prime
        if self.multiple is not None:
            expr = expr + '?' + self.multiple
        return expr


@dataclass(frozen=True)
class TranslatedMolecule:
    smi: str
    groups: str
    markush: bool
    sru: bool
    

class Translator:
    """A helper class for tokenizing, parsing, and reconstruction etc.."""

    @classmethod
    def parse_caption(
        cls, 
        caption: str, 
        return_mol: bool = False,
        error_msg: bool = False
    ) -> Optional[Tuple[Union[Chem.rdchem.Mol, str], str, str]]:
        """Parse a complete molecule caption or prediction."""
        smi, *trailings = caption.split(Tokens.separator)
        if len(trailings) != 1:
            if error_msg:
                logger.warning(
                    f'{len(trailings)} `{Tokens.separator}` found in caption: {caption}'
                )
            return
    
        if error_msg:
            RDLogger.EnableLog('rdApp.*')
        mol = Chem.MolFromSmiles(smi)
        RDLogger.DisableLog('rdApp.*')
        if mol is None:
            if error_msg:
                logger.warning(f'Invalid SMILES: {smi}')
            return
        
        # Split groups description and extension.
        groups, ext = cls.parse_trailing(trailings[0])
        
        if return_mol:
            return mol, groups, ext
        return smi, groups, ext
    
    @classmethod
    def parse_trailing(cls, trailing: str):
        """Parse the trailing part in caption into R group and extension."""
        matched = re.match(Patterns.trail_pattern, trailing)
        if matched is None:
            return '', ''
        content = matched.groupdict()
        return content.get('groups', ''), content.get('extension', '')
    
    @classmethod
    def parse_extension(cls, ext: str) -> str:
        """Parse extension info in caption."""
        # TODO
        return ext.strip('|')
            
    @classmethod
    def parse_groups(cls, seq: str) -> List[GroupDesc]:
        """Parse R group texts from predictions."""
        if seq == '':
            return []
        descriptions = []
        for grp_start, grp_content, _ in re.findall(Patterns.grp_pattern, seq):
            parsed = cls.parse_group(grp_content)
            if parsed is None:
                continue
            idx, grp_text = parsed
            if grp_start == Tokens.atom_start:
                grp_desc = GroupDesc(id=AtomIndex(idx))
                if len(grp_text) == 0:
                    grp_desc.is_dummy = True
            elif grp_start == Tokens.circ_start:
                grp_desc = GroupDesc(id=AtomIndex(idx), is_circle=True)
            elif grp_start == f'{Tokens.ring_start}{Tokens.circ_start}':
                grp_desc = GroupDesc(id=RingIndex(idx, virtual=True))
            elif grp_start == Tokens.ring_start:
                grp_desc = GroupDesc(id=RingIndex(idx))
            else:
                continue
            grp_desc.symbol = grp_text.get(TextType.SYMBOL)
            grp_desc.script = grp_text.get(TextType.SCRIPT)
            grp_desc.prime = grp_text.get(TextType.PRIME)
            grp_desc.multiple = grp_text.get(TextType.MULTIPLE)
            descriptions.append(grp_desc)
            
        return descriptions

    @classmethod
    def parse_group(cls, group: str) -> Optional[Tuple[int, Dict[TextType, str]]]:
        """Get text of a R group."""
        items = group.split(':')
        if len(items) != 2:
            return
        idx, content = items
        if not idx.isdigit():
            return
        idx = int(idx)
        if content == Tokens.dummy:
            return idx, {}
        # Gotta make sure that not all text types are empty string.
        grp_text = cls.get_group_texts(content)
        if len(grp_text) == 0:
            return
        
        return idx, grp_text
        
    @classmethod
    def get_group_texts(cls, content: str) -> Dict[TextType, str]:
        """Helper for reorganizing texts in R group."""
        texts = {}
        # NOTE Unmatched items will be empty strings.
        matched = re.match(Patterns.grp_content, content).groupdict()
        # print(matched)
        for tt_value, text in matched.items():
            if len(text) == 0:
                continue
            if tt_value == TextType.SYMBOL.value:
                texts[TextType.SYMBOL] = text
            elif tt_value == TextType.SCRIPT.value:
                # Remove square brackets.
                assert text.startswith('[') and text.endswith(']')
                texts[TextType.SCRIPT] = text[1:-1]
            elif tt_value == TextType.PRIME.value:
                texts[TextType.PRIME] = text
            elif tt_value == TextType.MULTIPLE.value:
                assert text.startswith('?')
                texts[TextType.MULTIPLE] = text[1:]
        return texts

    @classmethod
    def refactor(
        cls, 
        caption: str, 
        error_msg: bool = False
    ) -> Optional[TranslatedMolecule]:
        """Attempt to put R group abbreviations back into recognized molecule.
        Also check if caption represents a Markush molecule.
        # TODO: xifang 有时不能正确替代r基
        """
        parsed = cls.parse_caption(caption, return_mol=True, error_msg=error_msg)
        if parsed is None:
            return
        mol, groups, ext = parsed
        mol = Chem.RWMol(mol)
        
        to_remove = []
        is_markush = False  # flag for Markush structure
        is_sru = False  # flag for SRU structure
        
        if cls.parse_extension(ext) == 'Sg:n':
            is_sru = True
        
        for desc in cls.parse_groups(groups):
            # XXX We only care about `AbbrevGroup` for refactorization.
            if not desc.is_abbrev:
                is_markush = True
                continue
            i = int(desc.id)
            if not 0 <= i < mol.GetNumAtoms():
                continue
            atom = mol.GetAtomWithIdx(i)

            if atom.GetSymbol() != '*':
                continue
            # NOTE `AbbrevGroup` must connect to only one single bond.
            if atom.GetDegree() != 1:
                if error_msg:
                    logger.warning(
                        f'Group `{desc.symbol}` must have degree = 1 in {caption}'
                    )
                continue
            if any(not is_single_bond(bond) for bond in atom.GetBonds()):
                if error_msg:
                    logger.warning(
                        f'Group `{desc.symbol}` must link to single bond in {caption}'
                    )
                continue
            # Now it's merge time (modify target molecule in place).
            src = get_abbrev_smi().get(desc.symbol)
            if src is None:
                continue
            try:
                merge_group(tgt_mol=mol, src=src, attach_idx=i)
            except:
                continue
            else:
                to_remove.append(i)
        
        # Remove dummy atoms altogether in reverse order (will not affect added atoms).
        for i in sorted(to_remove, reverse=True):
            mol.RemoveAtom(i)
        
        # NOTE Must check validity of `translated` molecule.
        try:
            Chem.SanitizeMol(mol)
        except Exception as e:
            if error_msg:
                logger.error(str(e))
            return
        
        return TranslatedMolecule(
            smi=to_smiles(mol, canonical=True),
            groups=groups,
            markush=is_markush,
            sru=is_sru
        )

def get_refactor(res):
    try:
        return res.smi
    except:
        return ''


def get_new_smiles(pred_smiles, origin_molparser_smiles, molparser_smiles_extension):
    # input for this function only contain <a> in extension
    star_count = 0
    for s_idx, s in enumerate(origin_molparser_smiles):
        if s == '*':
            star_count += 1
    extension_list = molparser_smiles_extension.split('<a>')[1:]
    if len(extension_list) == 0:
        return origin_molparser_smiles

    mol = Chem.MolFromSmiles(origin_molparser_smiles)
    if mol is None:
        return pred_smiles
    star_mol_idx = []
    for i in range(mol.GetNumAtoms()):
        atom = mol.GetAtomWithIdx(i)
        symbol = atom.GetSymbol()
        # print(symbol)
        if symbol == '*':
            star_mol_idx.append(i)

    star_mol_idx_to_star_idx = {}
    for i, mol_idx in enumerate(star_mol_idx):
        star_mol_idx_to_star_idx[mol_idx] = i

    # print(star_mol_idx_to_star_idx)
    # print(origin_molparser_smiles)
    # print(molparser_smiles_extension)

    substitues= []
    star_new_rep = ['*' for i in range(star_count)]
    # filter out abbr
    for e_idx, e_item in enumerate(extension_list):
        mol_idx, e_content = int(e_item.split(':')[0]), e_item.split(':')[1].split('</a>')[0]
        if e_content not in abbr_to_smiles.keys():
            substitues.append((mol_idx, e_content))
    # print(substitues)

    if len(set([e_content[1] for e_content in substitues])) < 2:
        return pred_smiles

    substitues.sort(key=lambda x: x[1])
    for sort_idx, subs in enumerate(substitues):
        mol_idx = subs[0]
        if mol_idx in star_mol_idx_to_star_idx:
            star_idx = star_mol_idx_to_star_idx[mol_idx]
            star_new_rep[star_idx] = f'[{sort_idx+1}*]'
        else:
            return pred_smiles

    split_old_smiles = origin_molparser_smiles.split('*')
    assert len(split_old_smiles) == star_count + 1
    new_smiles = split_old_smiles[0]

    for idx in range(len(star_new_rep)):
        new_smiles += f'{star_new_rep[idx]}{split_old_smiles[idx+1]}'

    new_capation = new_smiles + '<sep>' + molparser_smiles_extension
    Translator.refactor(new_capation)

    return Translator.refactor(new_capation).smi