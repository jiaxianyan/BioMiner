import os 
import pandas as pd
import numpy as np
from tqdm import tqdm
from BioMiner import commons, runner
from rdkit import Chem
from rdkit import RDLogger

def merge_dictionaries(dict1_main, other_dicts):
  """Merges two dictionaries into a new dictionary.

  If there are overlapping keys, the values from dict2 will take precedence.

  Args:
    dict1: The first dictionary.
    dict2: The second dictionary.

  Returns:
    A new dictionary containing the merged key-value pairs.
  """

  merged_dict = dict1_main.copy()  # Create a copy to avoid modifying dict1
  for d in other_dicts:
    merged_dict.update(d)    # Update with dict2, overwriting keys from dict1
  return merged_dict


class resulter():

    def __init__(self, names, top_n, text_model_output_path, vision_model_output_path, 
                 structure_full_suffix, structure_part_suffix):
        self.top_n = top_n
        self.names = names
        self.text_model_output_path = text_model_output_path
        self.vision_model_output_path = vision_model_output_path
        self.structure_full_suffix = structure_full_suffix
        self.structure_part_suffix = structure_part_suffix

        self.bioactivity_modalities = ['_text', '_figure', '_table', '_image', '']
        self.structure_split = ['_entire', '_scaffold', '_chiral', '']
        self.bioactivity_only_sets = ['values', 'values_units', 'types_values', 'types_values_units']
        self.overall_task = ['_together']

        self.eval_results_total = {'name': []}

        return
    
    def initialize_evaluating_result(self):
        for modality in self.bioactivity_modalities:
            self.eval_results_total[f'recall{modality}_bioactivity_list'] = []
            self.eval_results_total[f'recall{modality}_bioactivity_list_total'] = []
            self.eval_results_total[f'precision{modality}_bioactivity_list'] = []
            self.eval_results_total[f'precision{modality}_bioactivity_list_total'] = []

        for split in self.structure_split:
            self.eval_results_total[f'recall{split}_structure_list'] = []
            self.eval_results_total[f'recall{split}_structure_list_total'] = []
            self.eval_results_total[f'precision{split}_structure_list'] = []
            self.eval_results_total[f'precision{split}_structure_list_total'] = []

            self.eval_results_total[f'recall{split}_coreference_structure_list'] = []
            self.eval_results_total[f'recall{split}_coreference_structure_list_total'] = []
            self.eval_results_total[f'precision{split}_coreference_structure_list'] = []
            self.eval_results_total[f'precision{split}_coreference_structure_list_total'] = []

        for task in self.overall_task:
            self.eval_results_total[f'recall{task}_list'] = []
            self.eval_results_total[f'recall{task}_list_total'] = []
            self.eval_results_total[f'precision{task}_list'] = []
            self.eval_results_total[f'precision{task}_list_total'] = []

        for setting in self.bioactivity_only_sets:
            self.eval_results_total[f'{setting}_recall_list'] = []
            self.eval_results_total[f'{setting}_recall_list_total'] = []
            self.eval_results_total[f'{setting}_precision_list'] = []
            self.eval_results_total[f'{setting}_precision_list_total'] = []

        self.eval_results_total['top_n_success_num'] = [0 for _ in range(self.top_n)]
        
        return

    def update_evaluating_result(self, name, evaluation_result):
        self.eval_results_total['name'].append(name)
        for modality in self.bioactivity_modalities:
            if evaluation_result[f'recall{modality}_bioactivity'] != -1:
                self.eval_results_total[f'recall{modality}_bioactivity_list'].append(evaluation_result[f'recall{modality}_bioactivity'])

            self.eval_results_total[f'recall{modality}_bioactivity_list_total'].append(evaluation_result[f'recall{modality}_bioactivity'])

            if evaluation_result[f'precision{modality}_bioactivity'] != -1:
                self.eval_results_total[f'precision{modality}_bioactivity_list'].append(evaluation_result[f'precision{modality}_bioactivity'])

            self.eval_results_total[f'precision{modality}_bioactivity_list_total'].append(evaluation_result[f'precision{modality}_bioactivity'])

        for split in self.structure_split:
            if evaluation_result[f'recall_coreference_structure{split}'] != -1:
                self.eval_results_total[f'recall{split}_coreference_structure_list'].append(evaluation_result[f'recall_coreference_structure{split}'])

            self.eval_results_total[f'recall{split}_coreference_structure_list_total'].append(evaluation_result[f'recall_coreference_structure{split}'])

            if evaluation_result[f'precision_coreference_structure{split}'] != -1:
                self.eval_results_total[f'precision{split}_coreference_structure_list'].append(evaluation_result[f'precision_coreference_structure{split}'])

            self.eval_results_total[f'precision{split}_coreference_structure_list_total'].append(evaluation_result[f'precision_coreference_structure{split}'])

            if evaluation_result[f'recall_structure{split}'] != -1:
                self.eval_results_total[f'recall{split}_structure_list'].append(evaluation_result[f'recall_structure{split}'])

            self.eval_results_total[f'recall{split}_structure_list_total'].append(evaluation_result[f'recall_structure{split}'])

            if evaluation_result[f'precision_structure{split}'] != -1:
                self.eval_results_total[f'precision{split}_structure_list'].append(evaluation_result[f'precision_structure{split}'])

            self.eval_results_total[f'precision{split}_structure_list_total'].append(evaluation_result[f'precision_structure{split}'])


        for task in self.overall_task:
            if evaluation_result[f'recall{task}'] != -1:
                self.eval_results_total[f'recall{task}_list'].append(evaluation_result[f'recall{task}'])

            self.eval_results_total[f'recall{task}_list_total'].append(evaluation_result[f'recall{task}'])

            if evaluation_result[f'precision{task}'] != -1:
                self.eval_results_total[f'precision{task}_list'].append(evaluation_result[f'precision{task}'])

            self.eval_results_total[f'precision{task}_list_total'].append(evaluation_result[f'precision{task}'])

        for setting in self.bioactivity_only_sets:
            if evaluation_result[f'{setting}_recall'] != -1:
                self.eval_results_total[f'{setting}_recall_list'].append(evaluation_result[f'{setting}_recall'])

            self.eval_results_total[f'{setting}_recall_list_total'].append(evaluation_result[f'{setting}_recall'])

            if evaluation_result[f'{setting}_precision'] != -1:
                self.eval_results_total[f'{setting}_precision_list'].append(evaluation_result[f'{setting}_precision'])

            self.eval_results_total[f'{setting}_precision_list_total'].append(evaluation_result[f'{setting}_precision'])

        for i in range(self.top_n):
            if evaluation_result['match_results'][i]:
                self.eval_results_total['top_n_success_num'][i] += 1

        save_failed_cases(name, 
                          evaluation_result['df_recall_failed_bioactivity'], 
                          evaluation_result['df_precision_failed_bioactivity'], 
                          evaluation_result['df_recall_failed_coreference_structure'], 
                          evaluation_result['df_precision_failed_coreference_structure'], 
                          self.text_model_output_path, 
                          self.vision_model_output_path, 
                          self.structure_full_suffix,
                          self.structure_part_suffix)

        return
    
    def output_evaluating_result(self):
        
        self.eval_results_total['name'].append('average')
        output_dict = {'name': self.eval_results_total['name']}
        for key in self.eval_results_total:
            # print(key)
            if key.endswith('total') or key in ['name', 'top_n_success_num']:
                # self.eval_results_total[f'{key}'].append('average')
                continue
            if len(self.eval_results_total[key]) != 0:
                temp_value = sum(self.eval_results_total[key])/len(self.eval_results_total[key])
            else:
                temp_value = -1
            print(f'Average {key}: {temp_value}')
            self.eval_results_total[key + '_total'].append(temp_value)
            output_dict[key] = self.eval_results_total[key + '_total']

        for i in range(self.top_n):
            temp_success = self.eval_results_total['top_n_success_num'][i]
            print(f'Top {i+1} align recall rate : {temp_success/len(self.names)}')

        
        pd.DataFrame(output_dict).to_csv(os.path.join(self.text_model_output_path, f'{self.structure_full_suffix}_{self.structure_part_suffix}_overall_metric.csv'))

        print('Valid Evaluate Num -- Affinity : ', len(self.eval_results_total['recall_bioactivity_list']), '/',len(self.names) )
        print('Valid Evaluate Num -- Structure : ', len(self.eval_results_total['recall_structure_list']), '/', len(self.names) )

        return


def save_failed_cases(name, 
                      df_recall_failed_bioactivity, df_precision_failed_bioactivity, 
                      df_recall_failed_coreference_structure, df_precision_failed_coreference_structure,
                      text_model_output_path, vision_model_output_path, 
                      structure_full_suffix, structure_part_suffix):

    df_recall_failed_bioactivity.to_csv(os.path.join(text_model_output_path, name, f'{name}_recall_failed_total_bioactivity.csv'))
    df_precision_failed_bioactivity.to_csv(os.path.join(text_model_output_path, name, f'{name}_precision_failed_total_bioactivity.csv'))
    df_recall_failed_coreference_structure.to_csv(os.path.join(vision_model_output_path, name, f'{name}_recall_failed_structure_{structure_full_suffix}_{structure_part_suffix}.csv'))
    df_precision_failed_coreference_structure.to_csv(os.path.join(vision_model_output_path, name, f'{name}_precision_failed_structure_{structure_full_suffix}_{structure_part_suffix}.csv'))

    return


def filter_structure_df_nan(df_extracted_structure_data):
    df_extracted_structure_data = df_extracted_structure_data[df_extracted_structure_data['ligand'].notna()]
    df_extracted_structure_data = df_extracted_structure_data[df_extracted_structure_data['smiles'].notna()]
    return df_extracted_structure_data


def filter_bioactivity_df_nan(df_extracted_bioactivity_data):
    df_extracted_bioactivity_data = df_extracted_bioactivity_data[df_extracted_bioactivity_data['ligand'].notna()]
    df_extracted_bioactivity_data = df_extracted_bioactivity_data[df_extracted_bioactivity_data['protein'].notna()]
    df_extracted_bioactivity_data = df_extracted_bioactivity_data[df_extracted_bioactivity_data['type'].notna()]
    df_extracted_bioactivity_data = df_extracted_bioactivity_data[df_extracted_bioactivity_data['value'].notna()]
    df_extracted_bioactivity_data = df_extracted_bioactivity_data[df_extracted_bioactivity_data['unit'].notna()]
    return df_extracted_bioactivity_data

def check_smiles_validity(smiles):
    RDLogger.DisableLog('rdApp.*')
    if isinstance(smiles, float):
        return False

    if '*' in smiles:
        return False

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return False
    
    if mol.GetNumAtoms() < 5:
        return False

    molecules = Chem.GetMolFrags(mol)
    if len(molecules) != 1:
        return False
    else:
        return True


def identifier_to_smiles(df_extracted_structure_data, df_extracted_bioactivity_data):
    # get extracted identifier-to-smiles mappling dict
    identifier_to_smiles = {}
    for (ligand_identifier_str, smiles) in zip(df_extracted_structure_data['ligand'].values.tolist(), 
                                               df_extracted_structure_data['smiles'].values.tolist()):
        if not isinstance(ligand_identifier_str, str):
            continue
        ligand_identifiers = ligand_identifier_str.split(';')
        for ligand_identifier in ligand_identifiers:
            identifier_to_smiles[ligand_identifier]= smiles

    # converting ligand identifier of bioactivity data into ligand smiles
    temp_smiles_list = []
    for ligand_identifier in df_extracted_bioactivity_data['ligand'].values:
        if ligand_identifier in identifier_to_smiles.keys():
            temp_smiles_list.append(identifier_to_smiles[ligand_identifier])
        else:
            temp_smiles_list.append(None)

    return temp_smiles_list
 

def is_float(string):
  try:
    float(string)
    return True
  except ValueError:
    return False

def unify_unit_pvalue(a_type, unit, value):        

    if a_type.lower() in ['pki', 'pkd', 'pic50']:
        return '', float(value.strip())

    if not is_float(value) or isinstance(unit, float):
        # print('do not unify unit')
        # print(f'{value} value.isdigit:{is_float(value)}')
        # print(f'{unit} isinstance(unit, float):{isinstance(unit, float)}')

        return unit, value
    
    unit = unit.lower()

    value = float(value)

    if unit == 'm':
        value = value * 1e9
    elif unit == 'mm':
        value = value * 1e6
    elif unit == 'um' or unit == 'μm' or unit == 'µm':
        value = value * 1e3
    elif unit == 'nm':
        value = value
    elif unit == 'pm':
        value = value * 1e-3
    else:
        # print(f'Invalid unit : {unit}')
        return unit, value
    
    return 'nm', str(value)

def unify_unit(unit, value):
    if not is_float(value) or isinstance(unit, float):
        # print('do not unify unit')
        # print(f'{value} value.isdigit:{is_float(value)}')
        # print(f'{unit} isinstance(unit, float):{isinstance(unit, float)}')

        return unit, value
    
    unit = unit.lower()

    value = float(value)

    if unit == 'm':
        value = value * 1e9
    elif unit == 'mm':
        value = value * 1e6
    elif unit == 'um' or unit == 'μm' or unit == 'µm':
        value = value * 1e3
    elif unit == 'nm':
        value = value
    elif unit == 'pm':
        value = value * 1e-3
    else:
        # print(f'Invalid unit : {unit}')
        return unit, value
    
    return 'nm', str(value)

def process_bioactivity_unit(unit):
    if isinstance(unit, float):
        return unit
    
    unit = unit.lower().strip()

    if unit == 'um' or unit == 'μm' or unit == 'µm':
        return 'um'

    return unit

def process_bioactivity_value(value):
    # process ±
    # print(value)
    if isinstance(value, float):
        # print(value)
        value = str(value)
    if isinstance(value, int):
        # print(value)
        value = str(value)
    value = value.replace(' ', '').split('±')[0]
    # print(value)

    # flag = ['>', '<', ]
    if value.startswith('>'):
        value = value[1:]
    
    if value.startswith('<'):
        value = value[1:]

    if value.startswith('='):
        value = value[1:]

    # print(value)

    return value


def check_valid_bioactivity_data(unit, value):
    # print('=================')
    # print(unit, value)
    value = process_bioactivity_value(value)

    unit, value = unify_unit(unit, value)
    # print('unified unit value:',unit, value)

    if is_float(value) and float(value) > 0 and unit == 'nm':
        # input('valid')
        return True
    else:
        # input('invalid')
        return False

def check_valid_bioactivity_type(type):
    if isinstance(type, float):
        return False
    
    type = type.lower()

    if type in ['ki','kd','ic50']:
        return True
    else:
        return False

def process_bioactivity_with_different_coreferences(df_bioactivity):
    df_bioactivity = df_bioactivity[df_bioactivity['ligand'].notna()]
    df_bioactivity = df_bioactivity[df_bioactivity['protein'].notna()]
    df_bioactivity = df_bioactivity[df_bioactivity['type'].notna()]
    df_bioactivity = df_bioactivity[df_bioactivity['value'].notna()]
    df_bioactivity = df_bioactivity[df_bioactivity['unit'].notna() | df_bioactivity['type'].str.lower().isin(['pic50','pki','pkd'])]

    ligands = df_bioactivity['ligand'].values.tolist()
    proteins = df_bioactivity['protein'].values.tolist()
    bioactivity_types = df_bioactivity['type'].values.tolist()
    values = df_bioactivity['value'].values.tolist()
    units = df_bioactivity['unit'].values.tolist()

    data_list, data_with_index_list = [], []

    for index, (l, p, a_t, v, u) in enumerate(zip(ligands, proteins, bioactivity_types, values, units)):

        # if not check_valid_bioactivity_data(l, p, a_t, v, u):
        #     continue

        v = process_bioactivity_value(v)
        u, v = unify_unit_pvalue(a_t,u, v)

        ls = l.split(';')
        ps = p.split(';')
        for p_n in ps:
            for l_n in ls:
                data_list.append((str(p_n).replace(' ', '').lower(), str(l_n).replace(' ', '').lower(), a_t.lower(), v, u))
                data_with_index_list.append(((str(p_n).replace(' ', '').lower(), str(l_n).replace(' ', '').lower(), a_t.lower(), v, u), index))
    
    # data_list = list(set(data_list))
    
    return data_list, data_with_index_list

    
def evaluate_bioactivity(df_bioactivity_labels, df_extracted_bioactivity_data):
    
    if len(df_bioactivity_labels) == 0:
        return -1, -1, df_bioactivity_labels, df_extracted_bioactivity_data

    if len(df_extracted_bioactivity_data) == 0:
        return 0, 0, df_bioactivity_labels, df_extracted_bioactivity_data

    processed_bioactivity_labels, processed_bioactivity_labels_with_index = process_bioactivity_with_different_coreferences(df_bioactivity_labels)
    processed_extracted_bioactivity, processed_extracted_bioactivity_with_index = process_bioactivity_with_different_coreferences(df_extracted_bioactivity_data)

    recall_index = []
    for bioactivity_data in processed_bioactivity_labels_with_index:
        data, index = bioactivity_data
        if data in processed_extracted_bioactivity:
            recall_index.append(index)

    precision_index = []
    for bioactivity_data in processed_extracted_bioactivity_with_index:
        data, index = bioactivity_data
        if data in processed_bioactivity_labels:
            precision_index.append(index)

    unique_recall_index = list(set(recall_index))
    unique_precision_index = list(set(precision_index))

    recall_rate = len(unique_recall_index)/len(df_bioactivity_labels)
    precision_rate = len(unique_precision_index)/len(df_extracted_bioactivity_data)

    recall_failed_index = []
    for i in range(len(df_bioactivity_labels)):
        if i not in unique_recall_index:
            recall_failed_index.append(i)

    precision_failed_index = []
    for i in range(len(df_extracted_bioactivity_data)):
        if i not in unique_precision_index:
            precision_failed_index.append(i)

    df_recall_failed_bioactivity = df_bioactivity_labels.iloc[recall_failed_index]
    df_precision_failed_bioactivity = df_extracted_bioactivity_data.iloc[precision_failed_index]

    return recall_rate, precision_rate, df_recall_failed_bioactivity, df_precision_failed_bioactivity


def process_structure_with_different_coreferences(df_structure):
    if len(df_structure) == 0:
        return [], []
    # df_structure = df_structure[df_structure['ligand'].notna()]
    df_structure = df_structure[df_structure['smiles'].notna()]

    ligands = df_structure['ligand'].values.tolist()
    smiles = df_structure['smiles'].values.tolist()

    data_list, data_with_index_list = [], []
    for index, (l, s) in enumerate(zip(ligands, smiles)):
        # print(l)
        if isinstance(l, float):
            ls = ['special_no_name']
        else:
            ls = l.split(';')
        for l_n in ls:
            data_list.append((str(l_n).replace(' ', '').lower(), s))
            data_with_index_list.append(((str(l_n).replace(' ', '').lower(), s), index))

    return data_list, data_with_index_list


def evaluate_structure(df_structure_labels, df_extracted_structure_data):
    if len(df_structure_labels) == 0:
        return -1, -1, -1, -1, df_structure_labels, df_extracted_structure_data
    
    if len(df_extracted_structure_data) == 0:
        return 0, 0, 0, 0, df_structure_labels, df_extracted_structure_data
    
    processed_structure_labels, processed_structure_labels_with_index = process_structure_with_different_coreferences(df_structure_labels)
    processed_extrected_structure, processed_extrected_structure_with_index = process_structure_with_different_coreferences(df_extracted_structure_data)

    structure_recall_index = []
    coreference_structure_recall_index = []
    for structure_data in processed_structure_labels_with_index:
        data, index = structure_data

        for extracted_structure_data in processed_extrected_structure:
            extracted_coreference, extracted_smiles = extracted_structure_data
            if data[0] == extracted_coreference and commons.process_mol.check_smiles_match(extracted_smiles, data[1]):
                coreference_structure_recall_index.append(index)
                break
        
        for extracted_structure_data in processed_extrected_structure:
            extracted_coreference, extracted_smiles = extracted_structure_data
            if commons.process_mol.check_smiles_match(extracted_smiles, data[1]):
                structure_recall_index.append(index)

    structure_precision_index = []
    coreference_structure_precision_index = []
    for structure_data in processed_extrected_structure_with_index:
        data, index = structure_data

        for extracted_structure_data in processed_structure_labels:
            extracted_coreference, extracted_smiles = extracted_structure_data
            if data[0] == extracted_coreference and commons.process_mol.check_smiles_match(extracted_smiles, data[1]):
                coreference_structure_precision_index.append(index)
                break
        
        for extracted_structure_data in processed_structure_labels:
            extracted_coreference, extracted_smiles = extracted_structure_data
            if commons.process_mol.check_smiles_match(extracted_smiles, data[1]):
                structure_precision_index.append(index)


    coreference_structure_recall_unique_index = list(set(coreference_structure_recall_index))
    structure_recall_unique_index = list(set(structure_recall_index))
    coreference_structure_precision_unique_index = list(set(coreference_structure_precision_index))
    structure_precision_unique_index = list(set(structure_precision_index))

    coreference_structure_recall_rate = len(coreference_structure_recall_unique_index)/len(df_structure_labels)
    structure_recall_rate = len(structure_recall_unique_index)/len(df_structure_labels)

    coreference_structure_precision_rate = len(coreference_structure_precision_unique_index)/len(df_extracted_structure_data)
    structure_precision_rate = len(structure_precision_unique_index)/len(df_extracted_structure_data)


    failed_coreference_structure_recall_index = []
    for i in range(len(df_structure_labels)):
        if i not in coreference_structure_recall_unique_index:
            failed_coreference_structure_recall_index.append(i)

    failed_coreference_structure_precision_index = []
    for i in range(len(df_extracted_structure_data)):
        if i not in coreference_structure_precision_unique_index:
            failed_coreference_structure_precision_index.append(i)

    df_recall_failed_coreference_structure = df_structure_labels.iloc[failed_coreference_structure_recall_index]
    df_precision_failed_coreference_structure = df_extracted_structure_data.iloc[failed_coreference_structure_precision_index]

    return coreference_structure_recall_rate, structure_recall_rate, \
           coreference_structure_precision_rate, structure_precision_rate, \
           df_recall_failed_coreference_structure, df_precision_failed_coreference_structure

def evaluate_recall(extracted_data, label_data):
    if len(label_data) == 0:
        return -1
    
    recall_num = 0
    for data in label_data:
        if data in extracted_data:
            recall_num += 1

    recall_rate = recall_num / len(label_data)
    
    return recall_rate


def evaluate_precision(extracted_data, label_data):
    if len(label_data) == 0:
        return -1
    if len(extracted_data) == 0:
        return 0
    
    precision_num = 0
    for data in extracted_data:
        if data in label_data:
            precision_num += 1
            
    precision_rate = precision_num / len(extracted_data)

    return precision_rate


def evaluate_bioactivity_only(df_bioactivity_labels, df_extracted_bioactivity_data):
    df_bioactivity_labels = df_bioactivity_labels.dropna(subset=['type', 'value', 'unit'])
    df_extracted_bioactivity_data = df_extracted_bioactivity_data.dropna(subset=['type', 'value', 'unit'])
    extracted_types, extracted_values, extracted_units = df_extracted_bioactivity_data['type'], df_extracted_bioactivity_data['value'], df_extracted_bioactivity_data['unit']
    label_types, label_values, label_units = df_bioactivity_labels['type'], df_bioactivity_labels['value'], df_bioactivity_labels['unit']

    extracted_types = [t.lower().strip() for t in extracted_types]
    extracted_values = [process_bioactivity_value(v) for v in extracted_values]
    extracted_units = [process_bioactivity_unit(u) for u in extracted_units]

    label_types = [t.lower().strip() for t in label_types]
    label_values = [process_bioactivity_value(v) for v in label_values]
    label_units = [process_bioactivity_unit(u) for u in label_units]

    unify_extracted_units = [unify_unit_pvalue(t, u, v)[0] for (t, u,v) in zip(extracted_types, extracted_units, extracted_values)]
    unify_extracted_values = [unify_unit_pvalue(t, u, v)[1] for (t, u,v) in zip(extracted_types, extracted_units, extracted_values)]

    unify_label_units = [unify_unit_pvalue(t, u, v)[0] for (t, u,v) in zip(label_types, label_units, label_values)]
    unify_label_values = [unify_unit_pvalue(t, u, v)[1] for (t, u,v) in zip(label_types, label_units, label_values)]



    # unified values only
    values_recall = evaluate_recall(unify_extracted_values, unify_label_values)
    values_precision = evaluate_precision(unify_extracted_values, unify_label_values)

    # value-unit 
    values_units_recall = evaluate_recall(list(zip(unify_extracted_values, unify_extracted_units)), list(zip(unify_label_values, unify_label_units)))
    values_units_precision = evaluate_precision(list(zip(unify_extracted_values, unify_extracted_units)), list(zip(unify_label_values, unify_label_units)))

    # type-value
    types_values_recall = evaluate_recall(list(zip(extracted_types, unify_extracted_values)), list(zip(label_types, unify_label_values)))
    types_values_precision = evaluate_precision(list(zip(extracted_types, unify_extracted_values)), list(zip(label_types, unify_label_values)))

    # type-value-unit
    types_values_units_recall = evaluate_recall(list(zip(extracted_types, unify_extracted_values, unify_extracted_units)), list(zip(label_types, unify_label_values, unify_label_units)))
    types_values_units_precision = evaluate_precision(list(zip(extracted_types, unify_extracted_values, unify_extracted_units)), list(zip(label_types, unify_label_values, unify_label_units)))

    return values_recall, values_precision, values_units_recall, values_units_precision, \
            types_values_recall, types_values_precision, types_values_units_recall, types_values_units_precision

def evaluate_bioactivity_structure_together(df_bioactivity_labels, df_extracted_bioactivity_data, 
                                         df_structure_labels, df_extracted_structure_data):

    if len(df_bioactivity_labels) == 0:
        return -1, -1, df_bioactivity_labels, df_extracted_bioactivity_data

    if len(df_extracted_bioactivity_data) == 0:
        return 0, 0, df_bioactivity_labels, df_extracted_bioactivity_data

    processed_bioactivity_labels, processed_bioactivity_labels_with_index = process_bioactivity_with_different_coreferences(df_bioactivity_labels)
    processed_extracted_bioactivity, processed_extracted_bioactivity_with_index = process_bioactivity_with_different_coreferences(df_extracted_bioactivity_data)

    processed_structure_labels, processed_structure_labels_with_index = process_structure_with_different_coreferences(df_structure_labels)
    processed_extrected_structure, processed_extrected_structure_with_index = process_structure_with_different_coreferences(df_extracted_structure_data)
    
    # get ligand_name_to_smiles_dict
    ligand_to_smiles = {}
    for data in processed_structure_labels:
        l, s = data
        ns = commons.process_mol.normalize_smiles(s)
        if ns is not None:
            ligand_to_smiles[l] = ns
    
    extracted_ligand_to_smiles = {}
    for data in processed_extrected_structure:
        l, s = data
        ns = commons.process_mol.normalize_smiles(s)
        if ns is not None:
            extracted_ligand_to_smiles[l] = ns

    # replace ligand_name to ligand_smiles
    processed_bioactivity_labels_smiles = []
    processed_bioactivity_labels_with_index_smiles = []
    processed_extracted_bioactivity_with_index_smiles = []
    processed_extracted_bioactivity_smiles = []

    for i in range(len(processed_bioactivity_labels)):
        data = processed_bioactivity_labels[i]
        p, l, t, v, u = data
        if l in ligand_to_smiles.keys():
            s = ligand_to_smiles[l]
            processed_bioactivity_labels_smiles.append((p, s, t, v, u))

    # assert len(processed_bioactivity_labels_smiles) == len(processed_bioactivity_labels)

    for i in range(len(processed_bioactivity_labels_with_index)):
        bioactivity_data = processed_bioactivity_labels_with_index[i]
        data, index = bioactivity_data
        p, l, t, v, u = data
        if l in ligand_to_smiles.keys():
            s = ligand_to_smiles[l]
            processed_bioactivity_labels_with_index_smiles.append(((p, s, t, v, u), index))
        
    # assert len(processed_bioactivity_labels_with_index_smiles) == len(processed_bioactivity_labels_with_index)

    for i in range(len(processed_extracted_bioactivity)):
        data = processed_extracted_bioactivity[i]
        p, l, t, v, u = data
        if l in extracted_ligand_to_smiles.keys():
            s = extracted_ligand_to_smiles[l]
            processed_extracted_bioactivity_smiles.append((p, s, t, v, u))

    for i in range(len(processed_extracted_bioactivity_with_index)):
        bioactivity_data = processed_extracted_bioactivity_with_index[i]
        data, index = bioactivity_data
        p, l, t, v, u = data
        if l in extracted_ligand_to_smiles.keys():
            s = extracted_ligand_to_smiles[l]
            processed_extracted_bioactivity_with_index_smiles.append(((p, s, t, v, u), index))

    if len(processed_bioactivity_labels_smiles) == 0:
        return -1, -1, df_bioactivity_labels, df_extracted_bioactivity_data

    if len(processed_extracted_bioactivity_smiles) == 0:
        return 0, 0, df_bioactivity_labels, df_extracted_bioactivity_data


    recall_index = []
    for bioactivity_data in processed_bioactivity_labels_with_index_smiles:
        data, index = bioactivity_data
        if data in processed_extracted_bioactivity_smiles:
            recall_index.append(index)

    precision_index = []
    for bioactivity_data in processed_extracted_bioactivity_with_index_smiles:
        data, index = bioactivity_data
        if data in processed_bioactivity_labels_smiles:
            precision_index.append(index)

    unique_recall_index = list(set(recall_index))
    recall_rate = len(unique_recall_index)/len(df_bioactivity_labels)

    
    unique_precision_index = list(set(precision_index))
    precision_rate = len(unique_precision_index)/len(df_extracted_bioactivity_data)

    recall_failed_index = []
    for i in range(len(df_bioactivity_labels)):
        if i not in unique_recall_index:
            recall_failed_index.append(i)

    precision_failed_index = []
    for i in range(len(df_extracted_bioactivity_data)):
        if i not in unique_precision_index:
            precision_failed_index.append(i)


    df_recall_failed_bioactivity = df_bioactivity_labels.iloc[recall_failed_index]
    df_precision_failed_bioactivity = df_extracted_bioactivity_data.iloc[precision_failed_index]

    return recall_rate, precision_rate, df_recall_failed_bioactivity, df_precision_failed_bioactivity

def filter_invalid_output_bioactivity(df):
    # first round: nan items
    df = filter_bioactivity_df_nan(df)

    # second round: invalid bioactivity value
    df['bioactivity_valid'] = [check_valid_bioactivity_data(u,v) for (v, u) in zip(df['value'], df['unit'])]
    df = df[df['bioactivity_valid']==True]

    return df

def filter_invalid_output_structure(df):
    
    # first round: nan items
    df = filter_structure_df_nan(df)
    # second round: invalid ligand structure
    
    df['smiles_valid'] = [check_smiles_validity(smi) for smi in df['smiles']]
    df = df[df['smiles_valid']==True]

    return df

def load_labels_and_results(name, labels_base_dir, dataset_name, text_model_output_path, 
                            vision_model_output_path, structure_full_suffix, structure_part_suffix,
                            bioactivity_text_suffix, bioactivity_image_suffix):
    
    label_path = os.path.join(labels_base_dir, dataset_name)
    df_bioactivity_labels = pd.read_csv(os.path.join(label_path, f'{name}_data.csv'), dtype=str)
    df_structure_labels = pd.read_csv(os.path.join(label_path, f'{name}_structure.csv'), dtype=str)
    df_structure_labels['chiral'] = ['@' in smi if isinstance(smi, str) else False for smi in df_structure_labels['smiles']]
    df_structure_labels['scaffold-substitute'] = [isinstance(smi, str) for smi in df_structure_labels['backbone']]
    df_structure_labels['norm'] = [not (c or s) for (c, s) in zip(df_structure_labels['chiral'], df_structure_labels['scaffold-substitute'])]

    df_extracted_text_bioactivity_data = pd.read_csv(os.path.join(text_model_output_path, name, f'{name}_text{bioactivity_text_suffix}_output.csv'), dtype=str)
    df_extracted_image_bioactivity_data = pd.read_csv(os.path.join(vision_model_output_path, name, f'{name}_image{bioactivity_image_suffix}_output.csv'), dtype=str)
    df_extracted_merge_bioactivity_data = pd.read_csv(os.path.join(text_model_output_path, name, f'{name}_merged{bioactivity_text_suffix}{bioactivity_image_suffix}_output.csv'), dtype=str)

    # save clean bioactivity data for evaluation and debug
    filter_bioactivity_df_nan(df_extracted_text_bioactivity_data).to_csv(os.path.join(text_model_output_path, name, f'{name}_text_output_clean.csv'))
    filter_bioactivity_df_nan(df_extracted_image_bioactivity_data).to_csv(os.path.join(vision_model_output_path, name, f'{name}_image_output_clean.csv'))
    filter_bioactivity_df_nan(df_extracted_merge_bioactivity_data).to_csv(os.path.join(text_model_output_path, name, f'{name}_merged_output_clean.csv'))

    df_extracted_text_bioactivity_data = pd.read_csv(os.path.join(text_model_output_path, name, f'{name}_text{bioactivity_text_suffix}_output.csv'), dtype=str)
    df_extracted_image_bioactivity_data = pd.read_csv(os.path.join(vision_model_output_path, name, f'{name}_image{bioactivity_image_suffix}_output.csv'), dtype=str)
    df_extracted_merge_bioactivity_data = pd.read_csv(os.path.join(text_model_output_path, name, f'{name}_merged{bioactivity_text_suffix}{bioactivity_image_suffix}_output.csv'), dtype=str)
    df_extracted_structure_data = pd.read_csv(os.path.join(vision_model_output_path, name, f'{name}_structure_merged_output_{structure_full_suffix}_{structure_part_suffix}.csv'), dtype=str)
    df_extracted_structure_full_data = pd.read_csv(os.path.join(vision_model_output_path, name, f'{name}_structure_full_output_{structure_full_suffix}.csv'), dtype=str)
    df_extracted_structure_part_data = pd.read_csv(os.path.join(vision_model_output_path, name, f'{name}_structure_part_output_{structure_part_suffix}.csv'), dtype=str)

    # filter invalid items for better precision result
    df_extracted_text_bioactivity_data = filter_invalid_output_bioactivity(df_extracted_text_bioactivity_data)
    df_extracted_image_bioactivity_data = filter_invalid_output_bioactivity(df_extracted_image_bioactivity_data)
    df_extracted_merge_bioactivity_data = filter_invalid_output_bioactivity(df_extracted_merge_bioactivity_data)
    df_extracted_structure_data = filter_invalid_output_structure(df_extracted_structure_data)
    df_extracted_structure_full_data = filter_invalid_output_structure(df_extracted_structure_full_data)
    df_extracted_structure_part_data = filter_invalid_output_structure(df_extracted_structure_part_data)
    
    df_extracted_structure_data['chiral'] = ['@' in smi if isinstance(smi, str) else False for smi in df_extracted_structure_data['smiles']]

    df_extracted_text_bioactivity_data.to_csv(os.path.join(text_model_output_path, name, f'{name}_text{bioactivity_text_suffix}_output_clean_new.csv'))
    df_extracted_image_bioactivity_data.to_csv(os.path.join(vision_model_output_path, name, f'{name}_image{bioactivity_image_suffix}_output_clean_new.csv'))
    df_extracted_merge_bioactivity_data.to_csv(os.path.join(text_model_output_path, name, f'{name}_merged{bioactivity_text_suffix}{bioactivity_image_suffix}_output_clean_new.csv'))
    df_extracted_structure_data.to_csv(os.path.join(vision_model_output_path, name, f'{name}_structure_merged_output_{structure_full_suffix}_{structure_part_suffix}_clean_new.csv'))
    df_extracted_structure_full_data.to_csv(os.path.join(vision_model_output_path, name, f'{name}_structure_full_output_{structure_full_suffix}_clean_new.csv'))
    df_extracted_structure_part_data.to_csv(os.path.join(vision_model_output_path, name, f'{name}_structure_part_output_{structure_part_suffix}_clean_new.csv'))

    loaded_results = {'df_bioactivity_labels':df_bioactivity_labels,
                      'df_structure_labels':df_structure_labels,
                      'df_extracted_text_bioactivity_data':df_extracted_text_bioactivity_data,
                      'df_extracted_image_bioactivity_data':df_extracted_image_bioactivity_data,
                      'df_extracted_bioactivity_data':df_extracted_merge_bioactivity_data,
                      'df_extracted_structure_data':df_extracted_structure_data,
                      'df_extracted_structure_full_data':df_extracted_structure_full_data,
                      'df_extracted_structure_part_data':df_extracted_structure_part_data}

    return loaded_results

def load_pdb_protein_name_ligand_smiles(pdb_name, pdb_structure_path):

    if not os.path.exists(os.path.join(pdb_structure_path, pdb_name)):
        pdb_name = pdb_name.split('_')[1]

    lig_path_mol2 = os.path.join(pdb_structure_path, pdb_name, f'{pdb_name}_ligand.mol2')
    lig_path_sdf = os.path.join(pdb_structure_path, pdb_name, f'{pdb_name}_ligand.sdf')
    
    if os.path.exists(lig_path_mol2) or os.path.exists(lig_path_sdf):
        m_lig = commons.process_mol.read_rdmol(lig_path_sdf, sanitize=True, remove_hs=True)
        if m_lig == None: 
            m_lig = commons.process_mol.read_rdmol(lig_path_mol2, sanitize=True, remove_hs=True)
        lig_smiles = Chem.MolToSmiles(m_lig)
    else:
        lig_smiles = None

    return lig_smiles, None

def get_pdb_label(pdb_name, pdb_name_path, pdb_label_path, pdb_structure_path):
    protein_name = commons.process_mol.get_protein_name(pdb_name_path, pdb_name)
    bioactivity_data = commons.process_mol.get_labels_from_name(pdb_label_path, pdb_name)

    lig_path_mol2 = os.path.join(pdb_structure_path, pdb_name, f'{pdb_name}_ligand.mol2')
    lig_path_sdf = os.path.join(pdb_structure_path, pdb_name, f'{pdb_name}_ligand.sdf')
    
    if os.path.exists(lig_path_mol2) and os.path.exists(lig_path_sdf):
        m_lig = commons.process_mol.read_rdmol(lig_path_sdf, sanitize=True, remove_hs=True)
        if m_lig == None: 
            m_lig = commons.process_mol.read_rdmol(lig_path_mol2, sanitize=True, remove_hs=True)
        lig_smiles = Chem.MolToSmiles(m_lig)
    else:
        lig_smiles = None

    pdb_labels = {'ligand_smiles': lig_smiles,
                  'protein_name': protein_name,
                  'bioactivity_data': bioactivity_data}

    # return lig_smiles, protein_name, bioactivity_data
    return pdb_labels
 
def align_given_complex_and_extracted_data(given_smiles, given_protein, df_extracted_data):
    similarity_result = []

    for i, (p, l, t, v, u) in enumerate(zip(df_extracted_data['protein'].values,
                                        df_extracted_data['ligand'].values, 
                                        df_extracted_data['type'].values, 
                                        df_extracted_data['value'].values,
                                        df_extracted_data['unit'].values)):
                
        similarity = commons.process_mol.calculate_similarity(l, given_smiles)
        similarity_result.append((similarity, (p, l, t, v, u)))

    similarity_result.sort(key=lambda x: x[0], reverse = True)

    return similarity_result

    # if len(max_result) == 1:
    #     return max_result[0][2:]
    # elif len(max_result) == 0:
    #     return '-1', '-1', '-1'
    # else:
    #     # select
    #     # client = runner.mllm.get_api_client(config.model.mllm)
    #     # align_prompt = 
    #     # data = runner.mllm.call_api_text(client, align_prompt, config.model.mllm, content)
    #     # print(max_result)
    #     return max_result[0][2:]

def evaluate_complex_match_step(given_smiles, given_protein, given_bioactivity_labels, 
                                df_extracted_bioactivity_data, df_extracted_structure_data, top_n):

    # 1. filter NaN of extracted structure data
    df_extracted_structure_data = df_extracted_structure_data.dropna()
    
    # 2. filter NaN of extracted bioactivity data
    df_extracted_bioactivity_data = df_extracted_bioactivity_data.dropna()

    # 3. converting ligand identifier of bioactivity data into ligand smiles
    df_extracted_bioactivity_data['ligand'] = np.array(identifier_to_smiles(df_extracted_structure_data, 
                                                                         df_extracted_bioactivity_data))

    # 4. unify label unit, removing >,<,=,...
    label_t, label_v, label_u = given_bioactivity_labels
    label_v = process_bioactivity_value(label_v)
    label_u, label_v = unify_unit_pvalue(label_t, label_u, label_v)

    # 5. currently, we only align the bioactivity label through ligand smiles similarity
    #    so, here, we calculate the similarity score based on ligand smiles for alingment.
    similarity_result = align_given_complex_and_extracted_data(given_smiles,
                                                               given_protein,
                                                               df_extracted_bioactivity_data)
    
    # 6. evaluate whether match
    match_results = []
    for top_n in range(1, top_n + 1):
        match_results.append(False)
        if len(similarity_result) == 0:
            continue
        for i in range(top_n):
            align_index = min(i, len(similarity_result) - 1)
            align_bioactivity = similarity_result[align_index]
            _, _, align_t, align_v, align_u = align_bioactivity[1]
            align_v = process_bioactivity_value(align_v)
            align_u, align_v = unify_unit_pvalue(align_t,align_u, align_v)
            if (align_t, align_v, align_u) == (label_t, label_v, label_u):
                match_results[-1] = True
                break

    return match_results

def evaluate_bioactivity_only_step(loaded_results):
    values_recall, values_precision, \
        values_units_recall, values_units_precision, \
            types_values_recall, types_values_precision, \
                types_values_units_recall, types_values_units_precision = evaluate_bioactivity_only(loaded_results['df_bioactivity_labels'], loaded_results['df_extracted_bioactivity_data'])
    
    bioactivity_only_result = {"values_recall":values_recall, 
                            "values_precision": values_precision, 
                            "values_units_recall": values_units_recall, 
                            "values_units_precision": values_units_precision, 
                            "types_values_recall":types_values_recall, 
                            "types_values_precision": types_values_precision, 
                            "types_values_units_recall": types_values_units_recall, 
                            "types_values_units_precision": types_values_units_precision}

    return bioactivity_only_result

def evaluate_structure_bioactivity_total_step(loaded_results):

    temp_res = evaluate_bioactivity_structure_together(loaded_results['df_bioactivity_labels'], 
                                                    loaded_results['df_extracted_bioactivity_data'], 
                                                    loaded_results['df_structure_labels'], 
                                                    loaded_results['df_extracted_structure_data'])

    total_eval_result = {'recall_together':temp_res[0],
                         'precision_together':temp_res[1],
                         'df_recall_together':temp_res[2],
                         'df_precision_together':temp_res[3]}
    
    return total_eval_result

def evaluate_structure_bioactivity_split_step(loaded_results):
    split_eval_result = {}
    bioactivity_modalities = {'text_':(['text'], 'text_'),
                            'figure_':(['figure'], 'image_'),
                            'table_':(['table'], 'image_'),
                            'image_':(['table','figure', 'image_'], 'image_'),
                            '':(['figure', 'table', 'text'],'')}
    
    df_bioactivity_labels = loaded_results['df_bioactivity_labels']
    for modality in bioactivity_modalities.keys():
        temp_res = evaluate_bioactivity(df_bioactivity_labels[df_bioactivity_labels['source'].isin(bioactivity_modalities[modality][0])], 
                                     loaded_results[f'df_extracted_{bioactivity_modalities[modality][1]}bioactivity_data'])
        
        split_eval_result[f'recall_{modality}bioactivity'] = temp_res[0]
        split_eval_result[f'precision_{modality}bioactivity'] = temp_res[1]
        split_eval_result[f'df_{modality}recall_failed_bioactivity'] = temp_res[2]
        split_eval_result[f'df_{modality}precision_failed_bioactivity'] = temp_res[3]

    structure_split = ['_entire', '_scaffold', '_chiral', '']
    df_structure_labels = loaded_results['df_structure_labels']
    df_extracted_structure_data = loaded_results['df_extracted_structure_data']
    for split in structure_split:
        if split == '_entire':
            temp_res = evaluate_structure(df_structure_labels[df_structure_labels['scaffold-substitute']==False],
                                          loaded_results['df_extracted_structure_full_data'])
        elif split == '_scaffold':
            temp_res = evaluate_structure(df_structure_labels[df_structure_labels['scaffold-substitute']==True],
                                         loaded_results['df_extracted_structure_part_data'])
        elif split == '_chiral':
            temp_res = evaluate_structure(df_structure_labels[df_structure_labels['chiral']==True],
                                          df_extracted_structure_data[df_extracted_structure_data['chiral']==True])
        elif split == '':
            temp_res = evaluate_structure(df_structure_labels, df_extracted_structure_data)
        
        split_eval_result[f'recall_coreference_structure{split}'] = temp_res[0]
        split_eval_result[f'recall_structure{split}'] = temp_res[1]
        split_eval_result[f'precision_coreference_structure{split}'] = temp_res[2]
        split_eval_result[f'precision_structure{split}'] = temp_res[3]
        split_eval_result[f'df_recall_failed_coreference_structure{split}'] = temp_res[4]
        split_eval_result[f'df_precision_failed_coreference_structure{split}'] = temp_res[5]

    return split_eval_result

def evaluate_step(name, pdb_name_path, pdb_label_path, pdb_structure_path,
                  labels_base_dir, dataset_name, text_model_output_path, vision_model_output_path, 
                  structure_full_suffix, structure_part_suffix, bioactivity_text_suffix, bioactivity_image_suffix, 
                  top_n):
    try:
        pdb_name = name.split('_')[1]
        pdb_labels = get_pdb_label(pdb_name, pdb_name_path, pdb_label_path, pdb_structure_path)        
        loaded_results = load_labels_and_results(name, labels_base_dir, dataset_name, 
                                                 text_model_output_path, vision_model_output_path, 
                                                 structure_full_suffix, structure_part_suffix,
                                                 bioactivity_text_suffix, bioactivity_image_suffix)
        split_eval_results = evaluate_structure_bioactivity_split_step(loaded_results)
        total_eval_results = evaluate_structure_bioactivity_total_step(loaded_results)
        bioactivity_only_results = evaluate_bioactivity_only_step(loaded_results)
        match_results = evaluate_complex_match_step(pdb_labels['ligand_smiles'], 
                                                    pdb_labels['protein_name'], 
                                                    pdb_labels['bioactivity_data'], 
                                                    loaded_results['df_extracted_bioactivity_data'],
                                                    loaded_results['df_extracted_structure_data'],
                                                    top_n)
    except Exception as e:
        raise ValueError(f'{name},{e}')
    
    eval_results = merge_dictionaries(split_eval_results, [total_eval_results, bioactivity_only_results] )
    eval_results['match_results'] = match_results
    return  eval_results
