from uu import Error
from builtins import ValueError, len
from traitlets import ValidateHandler
from BioMiner import commons
from PIL import Image
from openai import OpenAI
import pandas as pd
from rdkit import Chem, rdBase
from rdkit.Chem import DataStructs
from rdkit.Chem import Draw
from rdkit.Chem import AllChem
from rdkit import RDLogger
import requests
import json
import re
from io import StringIO
import sys
import sqlite3
from py2opsin import py2opsin

GPTSTPYEMODELS = ['gpt-4o', 'gpt-4o-mini', 'moonshot-v1-128k', 'gpt-4.1-mini']
IPUAC_FILE_PATH = 'BioMiner/commons/1d_r_groups/group_inpuc.log'
# RATIONALFORMULA_FILE_PATH = 'BioMiner/commons/1d_r_groups/group_chem_formula.log'
RATIONALFORMULA_FILE_PATH = 'BioMiner/commons/1d_r_groups/group_chem_formula_merge.log'
OTHER_FILE_PATH = 'BioMiner/commons/1d_r_groups/group_other_str.log'
IUPAC_DB_PATH = 'BioMiner/commons/1d_r_groups/iupac_cache.db'


def init_db():
    """初始化数据库表"""
    with sqlite3.connect(IUPAC_DB_PATH) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                iupac TEXT PRIMARY KEY,
                result TEXT
            )
        ''')
        # 开启 WAL 模式，大幅提升并发读写性能
        conn.execute('PRAGMA journal_mode=WAL;')

init_db()

def get_from_cache(iupac):
    """尝试从数据库读取"""
    with sqlite3.connect(IUPAC_DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT result FROM cache WHERE iupac = ?", (iupac,))
        row = cursor.fetchone()
        return row[0] if row else None

def save_to_cache(iupac, result):
    """写入数据库"""
    try:
        with sqlite3.connect(IUPAC_DB_PATH, timeout=30) as conn:
            # INSERT OR IGNORE 避免主键冲突报错
            conn.execute("INSERT OR IGNORE INTO cache (iupac, result) VALUES (?, ?)", (iupac, result))
    except Exception as e:
        print(f"Save error: {e}")

def get_api_client(mllm, base_url, api_key):
    if mllm == 'skip':
        return None

    if 'local' in mllm:
        client = OpenAI(base_url="http://localhost:8613/v1", 
                        api_key="EMPTY",
                        timeout=3600)
    else:
        client = OpenAI(base_url=base_url,
                        api_key=api_key)
    return client

def call_api_text(client, prompt, mllm, text_content, cot=False):
    if cot:
        prompt += '''\nLet's think step by step!'''
    
    try_times = 0
    while try_times < 1:
        try:
            if try_times > 0:
                print(f'{try_times}-th retry')

            if 'qwen' in mllm.lower() or 'biominer' in mllm.lower():
                response = client.chat.completions.create(messages=[{"role": "system", "content": "You are a scientific paper-reading assistant"}, 
                                                                    {"role": "user", "content": prompt + text_content}], 
                                                        model=mllm, temperature=0, max_tokens=4096)
            else:
                response = client.chat.completions.create(messages=[{"role": "system", "content": "You are a scientific paper-reading assistant"}, 
                                                                    {"role": "user", "content": prompt + text_content}], 
                                                        model=mllm, temperature=0, response_format={"type": "json_object"}, max_tokens=4096)
                
            output = response.choices[0].message.content
            return output
        except Exception as e:
            # may confront with maximum length error with gpt-4
            print(f'{mllm} {try_times} try failed:', e)
            try_times += 1

    return  '[]'    

def call_api_iamge(client, prompt, mllm, image, cot=False):
    if cot:
        prompt += '''\nLet's think step by step!'''
    # print(prompt)
    try_times = 0
    while try_times < 1:
        try:
            image_data = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image}", "detail": "high"}}
            text_data = {"type": "text","text": prompt}
            if 'qwen' in mllm.lower() or 'biominer' in mllm.lower():
                response = client.chat.completions.create(messages=[{"role": "system", "content": "You are a expert with certian knowledge of bioinfomratics and chemistry. Please help finish these domain related paper-reading tasks."}, 
                                                                    {"role": "user", "content": [image_data, text_data]}],
                                                            model=mllm, temperature=0, max_tokens=4096)
            else:
                response = client.chat.completions.create(messages=[{"role": "system", "content": "You are a expert with certian knowledge of bioinfomratics and chemistry. Please help finish these domain related paper-reading tasks."}, 
                                                                    {"role": "user", "content": [image_data, text_data]}],
                                                            model=mllm, temperature=0, response_format={"type": "json_object"}, max_tokens=4096)
            output = response.choices[0].message.content
            return output
        except Exception as e:
            # may confront with maximum length error with gpt-4
            print(f'{mllm} {try_times} try failed:', e)
            try_times += 1

    return  '[]'

def process_api_output(output):
    if '`'in output:
        try:
            output = output.replace('json', '').split("```")[1]
        except:
            output = '[]'
        
    return output

def full_structure_data_api_putput_to_list(data, mllm, index2smiles):
    data_list = []
    if mllm in GPTSTPYEMODELS:
        if 'data' not in data:
            return data_list
        data = data['data']

    for item in data:
        if isinstance(item, dict) and 'index' in item.keys() and 'identifier' in item.keys():
            if item['index'] in index2smiles.keys():
                extracted_info = {"identifier": item['identifier'],
                                  "smiles": index2smiles[item['index']]}
                data_list.append(extracted_info)

    return data_list

def convert_molminer_scaffold_smiles_for_zip(backbone):
    start_count = 0
    for s in backbone:
        if s =='*':
            start_count += 1
    
    if start_count == 1:
        backbone = backbone.replace(f'*', f'[*:1]')
    else:
        for i in range(start_count):
            backbone = backbone.replace(f'[{i+1}*]', f'[*:{i+1}]')

    return backbone, start_count


def convert_molminer_substitute_smiles_for_zip(group_smi, idx):
    if group_smi is None:
        return None
    
    start_count = 0
    for s in group_smi:
        if s =='*':
            start_count += 1
    
    if start_count != 1:
        return None

    group_smi = group_smi.replace(f'*', f'[*:{idx}]')

    return group_smi

def is_float(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
  

def is_chem_formula(string):
    with open(RATIONALFORMULA_FILE_PATH, 'r') as f:
        json_data = json.load(f)    
    if string in json_data.keys():
        return True
    return False


def is_iupac(iupac):
    # with open(IPUAC_FILE_PATH, 'r') as f:
    #     iupac_json_data = json.load(f)

    # if iupac in iupac_json_data.keys():
    #     return True
    # else:
    #     return False

    cached_smiles = get_from_cache(iupac)
    if cached_smiles:
        return True

    smiles_strings = py2opsin(
        chemical_name = iupac.replace('/',''),
        output_format = "SMILES",
        allow_radicals = True
    )
    if smiles_strings is None or len(smiles_strings) == 0:
        return False
    else:
        return True

    # path = "https://opsin.ch.cam.ac.uk/opsin/"            # URL path to the OPSIN API
    # apiurl = path + iupac + '.json'                 # concatenate (join) strings with the '+' operator
    # reqdata = requests.get(apiurl)                        # get is a method of request data from the OPSIN server
    # jsondata = reqdata.json()                             # get the downloaded JSON
    # if not jsondata['status'] == 'SUCCESS':
    #     return False
    # else:
    #     return True
    #     smiles = jsondata['smiles']
    #     iupac_json_data[iupac] = smiles
    #     new_json_data = json.dumps(iupac_json_data, indent=4)
    #     with open(IPUAC_FILE_PATH, 'w') as f:
    #         f.write(new_json_data)
    #     return True

def convert_molminer_substitue_iupac_for_zip(group_iupac, idx):
    # with open(IPUAC_FILE_PATH, 'r') as f:
    #     iupac_json_data = json.load(f)
    # # del jsondata['cml']                                   # remove the cml element of the JSON for nicer display
    # # print(json.dumps(jsondata, indent=4))                 # print the JSON in a nice format
    # # print(group_iupac)
    # # print(iupac_json_data)
    # smiles = iupac_json_data[group_iupac]

    cached_smiles = get_from_cache(group_iupac)
    if cached_smiles:
        # print(f"Cache Hit: {group_iupac}")
        # 注意：这里存的是最终结果还是中间结果看你需求。
        # 如果存的是 origin_smiles，需要在这里重新做一下 idx 的替换逻辑
        # 假设我们缓存的是处理完 idx 之前的 origin_smiles
        origin_smiles = cached_smiles
    else:
        # path = "https://opsin.ch.cam.ac.uk/opsin/"            # URL path to the OPSIN API
        # apiurl = path + group_iupac + '.json'                 # concatenate (join) strings with the '+' operator
        # reqdata = requests.get(apiurl)                        # get is a method of request data from the OPSIN server
        # jsondata = reqdata.json()                             # get the downloaded JSON
        # origin_smiles = jsondata['smiles']

        origin_smiles = py2opsin(
            chemical_name = group_iupac.replace('/',''),
            output_format = "SMILES",
            allow_radicals=True
        )
        if origin_smiles is not None and len(origin_smiles) > 0:
            # 3. 写入缓存
            save_to_cache(group_iupac, origin_smiles)

    # smiles = origin_smiles.replace('[CH3]', '[C]')
    # smiles = origin_smiles.replace('[CH2]', '[C]')
    # smiles = smiles.replace('[CH]', '[C]')
    # smiles = smiles.replace('[NH]', '[N]')
    # new_smiles = re.sub(r'\[(.)\]', rf'\1([*:{idx}])', smiles).strip()

    smiles = origin_smiles.replace('[CH3]', '[C]')
    smiles = smiles.replace('[CH2]', '[C]')
    smiles = smiles.replace('[CH]', '[C]')
    smiles = smiles.replace('[NH]', '[N]')

    if group_iupac == 'TBDMS':
        new_smiles = f'[Si]([*:{idx}])(C)(C)C(C)(C)C'
    elif group_iupac == 'TBDPS':
        new_smiles = f'[Si]([*:{idx}])(C1=CC=CC=C1)(C1=CC=CC=C1)C(C)(C)C'
    elif group_iupac == 'nitro':
        new_smiles = f'[N+]([*:{idx}])(=O)[O-]'
    elif group_iupac == 'hydroxyl':
        new_smiles = f'O([*:{idx}])[H]'
    else:
        new_smiles = re.sub(r'\[(.)\]', rf'\1([*:{idx}])', smiles).strip()

    start_count = 0
    for s in new_smiles:
        if s =='*':
            start_count += 1
    if new_smiles == smiles:
        print(f'no change, {group_iupac} -> {origin_smiles}')

    if start_count > 1:
        print(f'more than one connetion points, {group_iupac} -> {origin_smiles}')
        return None
    elif start_count == 0:
        print(f'no connection point, {group_iupac} -> {origin_smiles}')
        return None

    return new_smiles

def convert_molminer_formula_for_zip(group_chem_formula, idx):
    with open(RATIONALFORMULA_FILE_PATH, 'r') as f:
        json_data = json.load(f)    
    
    smiles = json_data[group_chem_formula]
    smiles = smiles.replace('*', f'[*:{idx}]')
    return smiles

def molparser_part_structure_data_api_putput_to_list():


    return

def convert_molparser_smiles_for_zip():

    return

def zip_molecule(backbone_groups):
    RDLogger.DisableLog('rdApp.*')
    try:
        molecule_unzipped = Chem.MolFromSmiles(backbone_groups)
        molecule_zipped = Chem.molzip(molecule_unzipped)
        smiles = Chem.MolToSmiles(molecule_zipped)
    except Exception as e:
        smiles =  None
    
    return smiles
    
def part_structure_data_api_putput_to_list(data, mllm, index2smiles):
    data_list = []
    if mllm in GPTSTPYEMODELS:
        if 'data' not in data:
            return data_list
        data = data['data']

    # print(data)
    for item in data:
        if (isinstance(item, dict) and 'scaffold' in item.keys() and 'identifier' in item.keys() and 'R-group' in item.keys()):
            backbone_index = item['scaffold']
            identifier = item['identifier']
            groups_index = item['R-group']
            
            if not isinstance(backbone_index, str) or not isinstance(groups_index, dict) or backbone_index not in index2smiles.keys():
                continue
            
            backbone = index2smiles[backbone_index]
            if backbone is None:
                continue
            backbone, start_count = convert_molminer_scaffold_smiles_for_zip(backbone)
            group_names = list(groups_index.keys())
            group_names.sort()

            if len(group_names) != start_count:
                continue
            
            groups, invalid_group = [], False

            for idx, group_name in enumerate(group_names):
                group_smi_index = groups_index[group_name]
                if not isinstance(group_smi_index, str):
                    invalid_group = True
                    break

                if group_smi_index in index2smiles.keys():
                    group_smi = index2smiles[group_smi_index]
                    group_smi = convert_molminer_substitute_smiles_for_zip(group_smi, idx+1)
                else:
                    try:
                        if is_float(group_smi_index):
                            invalid_group = True
                            with open('group_float_invalid.log', 'a+') as f:
                                f.write(f'{group_smi_index}\n')
                            break  
                        elif is_chem_formula(group_smi_index):
                            group_smi = convert_molminer_formula_for_zip(group_smi_index, idx+1)     
                        elif is_iupac(group_smi_index):
                            group_smi = convert_molminer_substitue_iupac_for_zip(group_smi_index, idx+1)
                        else:
                            with open(OTHER_FILE_PATH, 'r') as f:
                                others = json.load(f)
                            if group_smi_index not in others.keys():
                                others[group_smi_index] = ""
                                other_json_data = json.dumps(others, indent=4)
                                with open(OTHER_FILE_PATH, 'w') as f:
                                    f.write(other_json_data)
                            invalid_group = True
                            break
                    except:
                        invalid_group = True
                        break

                if group_smi == f'[*:{idx+1}]H':
                    if f'([*:{idx+1}])' in backbone:
                        backbone = backbone.replace(f'([*:{idx+1}])', '')
                    else:
                        backbone = backbone.replace(f'[*:{idx+1}]', '')
                else:
                    groups.append(group_smi)

            for smi in [backbone] + groups:
                if smi is None:
                    invalid_group = True
                    break
            if invalid_group:
                continue 
            
            zip_smiles_input = '.'.join([backbone] + groups)
            smiles = zip_molecule(zip_smiles_input)
            # print(f'zip input: {zip_smiles_input}, zip output: {smiles}')

            extracted_info = {"identifier": identifier,"smiles": smiles}
            data_list.append(extracted_info)

    return data_list

def bioactivity_data_api_output_to_list(data, mllm):
    data_list = []
    if mllm in GPTSTPYEMODELS:
        if 'data' not in data:
            return data_list
        data = data['data']

    for item in data:
        if isinstance(item, dict) and 'protein' in item.keys() and 'ligand' in item.keys() and 'affinity' in item.keys():
            if isinstance(item["affinity"], dict) and 'type' in item["affinity"].keys() and 'value' in item["affinity"].keys() and 'unit' in item["affinity"].keys():
                extracted_info = {"protein": item["protein"], 
                                "ligand": item["ligand"],
                                "affinity": {"type": item["affinity"]["type"],"value": item["affinity"]["value"],"unit": item["affinity"]["unit"]}}
                data_list.append(extracted_info)

    return data_list

def bioactivity_data_list_to_dict(data_list):
    data_dict = {'protein': [], 'ligand': [], 'type': [], 'value': [], 'unit': []}

    for item in data_list:
        data_dict["protein"].append(item["protein"])
        data_dict["ligand"].append(item["ligand"])
        data_dict["type"].append(item["affinity"]["type"])
        data_dict["value"].append(item["affinity"]["value"])
        data_dict["unit"].append(item["affinity"]["unit"])

    return data_dict

def structure_data_list_to_dict(data_list):
    data_dict = {'ligand': [], 'smiles': []}
    for item in data_list:
        # print(item)
        data_dict["ligand"].append(item["identifier"])
        data_dict["smiles"].append(item["smiles"])

    return data_dict

def bioactivity_data_df_to_list(data_df):
    data_list = []
    proteins, ligands, types, values, units = data_df['protein'].values.tolist(), data_df['ligand'].values.tolist(), data_df['type'].values.tolist(), data_df['value'].values.tolist(), data_df['unit'].values.tolist()
    for (p, l, t, v, u) in zip(proteins, ligands, types, values, units):
        data_list.append({'protein': p, 'ligand': l, 'affinity':{'type':t, 'value':v, 'unit': u}})

    return data_list
