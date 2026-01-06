import json
import ssl
import csv
import os
import re
import pandas as pd
from rdkit import Chem
from pubchempy import get_compounds
from rdkit.Chem import DataStructs
from rdkit.Chem import AllChem
import warnings

def replace_group(smiles):

    mol = Chem.MolFromSmiles(smiles)

    if mol:
        for atom in mol.GetAtoms():
            if atom.GetSymbol() == '*' and atom.GetIsotope() == 1:
                atom.SetIsotope(0)
                break

        new_smiles = Chem.MolToSmiles(mol)
        return new_smiles
    else:
        return smiles
    
def neutralize_smiles(smi):
    mol = Chem.MolFromSmiles(smi)
    pattern = Chem.MolFromSmarts("[+1!h0!$([*]~[-1,-2,-3,-4]),-1!$([*]~[+1,+2,+3,+4])]")
    at_matches = mol.GetSubstructMatches(pattern)
    at_matches_list = [y[0] for y in at_matches]
    if len(at_matches_list) > 0:
        for at_idx in at_matches_list:
            atom = mol.GetAtomWithIdx(at_idx)
            chg = atom.GetFormalCharge()
            hcount = atom.GetTotalNumHs()
            atom.SetFormalCharge(0)
            atom.SetNumExplicitHs(hcount - chg)
            atom.UpdatePropertyCache()
    return Chem.MolToSmiles(mol)

def smiles_to_canosmiles(smiles):
    mol = Chem.MolFromSmiles(smiles)
    return Chem.MolToSmiles(mol, canonical=True)

def normalize_smiles(smiles):
    try:
        nsmiles = neutralize_smiles(smiles)
        cnsmiles = smiles_to_canosmiles(nsmiles)
        return cnsmiles
    except:
        return None

def check_smiles_match(smia, smib):
    try:
        nsmia = neutralize_smiles(smia)
        nsmib = neutralize_smiles(smib)
        cnsmia = smiles_to_canosmiles(nsmia)
        cnsmib = smiles_to_canosmiles(nsmib)
        return replace_group(cnsmia) == replace_group(cnsmib)
    except:
        return False
    
def convert_to_smiles(group):
    with open('./functional_groups_cache.json', 'r') as f:
        r_group_dict = json.load(f)
        
    if group is None:
        return ''
    if isinstance(group, str) and '-' in group:
        group = group.replace("-", "")
        
    if group in r_group_dict:
        return r_group_dict[group]
    else:
        ssl._create_default_https_context = ssl._create_unverified_context
    try:
        m = get_compounds('CH3' + group, 'formula')
        smiles = m[0].canonical_smiles
        r_group_dict.append(
            {
                group: smiles[1:]
            }
        )
        with open('./functional_groups_cache.json', 'w') as f:
            json.dump(r_group_dict, f)
        return smiles[1:]
    except:
        return ""


def zip_molecule(backbone, groups, convert_flags=None):
    backbone_groups = backbone
    for i, group in enumerate(groups):
        if convert_flags[i]: 
            backbone_groups += '.' + f"[*:{i + 1}]" + convert_to_smiles(group)
        else:
            if isinstance(group, str):
                backbone_groups += '.' + group

    # print(f'bakcbone: {backbone}, groups: {groups}')``
    # print(f"before molzip: {backbone_groups}")

    # print(backbone_groups)
    try:
        molecule_unzipped = Chem.MolFromSmiles(backbone_groups)
        molecule_zipped = Chem.molzip(molecule_unzipped)
        smiles = Chem.MolToSmiles(molecule_zipped)
    except:
        return "NA"
    
    return smiles


def calculate_similarity(smiles1, smiles2):
    try:
        mol1 = Chem.MolFromSmiles(smiles1)
        mol2 = Chem.MolFromSmiles(smiles2)

        if mol1 is None or mol2 is None:
            return -1
        
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 2, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 2, nBits=2048)

        return DataStructs.TanimotoSimilarity(fp1, fp2)
    except:
        return -1
    
def read_rdmol(molecule_file, sanitize=False, calc_charges=False, remove_hs=False):
    if molecule_file.endswith('.mol2'):
        mol = Chem.MolFromMol2File(molecule_file, sanitize=False, removeHs=False)
    elif molecule_file.endswith('.sdf'):
        supplier = Chem.SDMolSupplier(molecule_file, sanitize=False, removeHs=False)
        mol = supplier[0]
    elif molecule_file.endswith('.pdbqt'):
        with open(molecule_file) as file:
            pdbqt_data = file.readlines()
        pdb_block = ''
        for line in pdbqt_data:
            pdb_block += '{}\n'.format(line[:66])
        mol = Chem.MolFromPDBBlock(pdb_block, sanitize=False, removeHs=False)
    elif molecule_file.endswith('.pdb'):
        mol = Chem.MolFromPDBFile(molecule_file, sanitize=False, removeHs=False)
    else:
        return ValueError('Expect the format of the molecule_file to be '
                          'one of .mol2, .sdf, .pdbqt and .pdb, got {}'.format(molecule_file))

    try:
        if sanitize or calc_charges:
            Chem.SanitizeMol(mol)

        if calc_charges:
            # Compute Gasteiger charges on the molecule.
            try:
                AllChem.ComputeGasteigerCharges(mol)
            except:
                warnings.warn('Unable to compute charges for the molecule.')

        if remove_hs:
            mol = Chem.RemoveHs(mol, sanitize=sanitize)
    except:
        return None

    return mol


def get_protein_name(names_path, name):
    with open(names_path, 'r') as f:
        lines = f.read().strip().split('\n')[6:]
    res = {}

    for line in lines:
        temp = line.split()
        pdb_id, protein_name = temp[0], temp[3:]
        res[pdb_id] = ' '.join(protein_name)

    if name in res.keys():
        return res[name]
    else:
        return None


def get_labels_from_name(lables_path, name):
    with open(lables_path, 'r') as f:
        lines = f.read().strip().split('\n')[6:]
    res = {}

    for line in lines:
        temp = line.split()
        pdb_id, bioactivity_data = temp[0], temp[4]
        res[pdb_id] = bioactivity_data

    if name in res.keys():
        temp_label = res[name]

        if '=' in temp_label:
            items = temp_label.split('=')
        elif '>' in temp_label:
            items = temp_label.split('>')
        elif '<' in temp_label:
            items = temp_label.split('<')
        elif '~' in temp_label:
            items = temp_label.split('~')
        else:
            print(temp_label)

        type, value, unit = items[0], items[1][:-2], items[1][-2:]

        return (type, value, unit)
    else:
        return None