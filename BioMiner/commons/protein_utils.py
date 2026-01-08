
import requests
import json
import os 
from bs4 import BeautifulSoup
from urllib.parse import quote
# from rcsbsearchapi import TextQuery, AttributeQuery
import urllib.request
import xml.etree.ElementTree as ET
from openai import OpenAI

def get_alphafold_db_structure(uniprot_id, save_file=False):
    base_url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"

    try:
        response = requests.get(base_url)
        response.raise_for_status()  # Raise an exception for bad status codes

        data = response.json()

        if data:
            structure_data = data[0]['pdb']

            if save_file:
                file_path = f"{uniprot_id}_alphafold.pdb"
                with open(file_path, "w") as f:
                    f.write(structure_data)
                print(f"AlphaFold structure saved to {file_path}")
                return structure_data, file_path
            else:
                return structure_data
        else:
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error: Could not extract structure data from API response. {e}")
        return None


def get_pdb_id(uniprot_id):
    try:
        base_url = f"https://www.ebi.ac.uk/pdbe/api/mappings/best_structures/{uniprot_id}"
        response = requests.get(base_url)
        response.raise_for_status()
        data = response.json()
        # print(data.keys())
        return data[uniprot_id][0]['pdb_id']
    except:

        return None


def get_uniprot_name_ttd(protein_name, organism=None):
    with open('BioMiner/data/P2-01-TTD_uniprot_all.txt', 'r') as f:
        lines = f.read().strip().split('\n')[22:]

    uniprot_names = []
    TARGNAME_to_UNIPROID = {}
    for index in range(0, len(lines), 5):
        # print(index)
        UNIPROID = lines[index + 1][8:].strip()
        TARGNAME = lines[index + 2][8:].strip()
        TARGNAME_to_UNIPROID[TARGNAME] = UNIPROID
        # input(UNIPROID)
        # input(TARGNAME)

    for key in TARGNAME_to_UNIPROID.keys():
        if protein_name.lower() in key.lower():
            # print(TARGNAME_to_UNIPROID[key])
            uniprot_names.append(TARGNAME_to_UNIPROID[key])

    if len(uniprot_names) > 0:
        return uniprot_names[0]
    else:
        return None

def map_uniprot_id_ttd(uniprot_name):

    base_url = f"https://rest.uniprot.org/uniprotkb/search?query=id:{uniprot_name}"
    all_fastas = requests.get(base_url).text
    data = json.loads(all_fastas)
    if data['results']:
        uniprot_ids = [entry['primaryAccession'] for entry in data['results']]
        # print(uniprot_ids)
        return uniprot_ids[0]
    else:
        return None
    

def get_uniprot_id_rest_api(protein_name):
    base_url = f"https://rest.uniprot.org/uniprotkb/search?query=protein_name:{protein_name}"
    all_fastas = requests.get(base_url).text
    data = json.loads(all_fastas)
    print(data)
    if data['results']:
        uniprot_ids = [entry['primaryAccession'] for entry in data['results']]
        print(uniprot_ids)
        return uniprot_ids
    else:
        return None

def get_uniprot_id_based_on_name_ttd(protein_name):
    uniprot_name = get_uniprot_name_ttd(protein_name)
    if uniprot_name is not None:
        uniprot_id = map_uniprot_id_ttd(uniprot_name)
        return uniprot_id
    else:
        return None
    
def pdb_structure_based_on_uniprot_id(uniprot_id):
    pdb_id = get_pdb_id(uniprot_id)
    if pdb_id is None:
        return None
    
    save_path = f'./pdb/{uniprot_id}/{pdb_id}.pdb'

    if not os.path.exists(f'./pdb/{uniprot_id}'):
        os.makedirs(f'./pdb/{uniprot_id}')

    if not os.path.exists(save_path):
        os.system(f'wget https://files.rcsb.org/download/{pdb_id}.pdb')
        os.system(f'mv {pdb_id}.pdb {save_path}')
    
    if not os.path.exists(save_path):
        return None
    print(f'Successfully downloaded pdb structure for {uniprot_id} to {save_path}')
    return save_path

def pdb_structure_based_on_pdb(pdb_id):

    save_path = f'./pdb/{pdb_id}/{pdb_id}.pdb'

    if not os.path.exists(f'./pdb/{pdb_id}'):
        os.makedirs(f'./pdb/{pdb_id}')

    if not os.path.exists(save_path):
        os.system(f'wget https://files.rcsb.org/download/{pdb_id}.pdb')
        os.system(f'mv {pdb_id}.pdb {save_path}')
    
    if not os.path.exists(save_path):
        return None
    print(f'Successfully downloaded pdb structure for {pdb_id} to {save_path}')
    return save_path

def query_pdb_by_protein_name(protein_name):

    # Search for structures associated with the phrase "Hemoglobin"
    query = AttributeQuery(attribute='struct.title',
                           operator="contains_phrase", 
                           value=protein_name)
    results = query()
    # print(list(results))
    return list(results)

def query_uniprot_id_by_protein_name(protein_name):
    try:
        # Encode the protein name for the URL
        encoded_protein_name = quote(protein_name)

        # Construct the UniProt query URL (using REST API)
        url = f"https://rest.uniprot.org/uniprotkb/stream?query=protein_name:{encoded_protein_name}&format=xml"
        
        # Make the request to UniProt
        with urllib.request.urlopen(url) as response:
            xml_data = response.read()

        # Parse the XML data
        root = ET.fromstring(xml_data)

        # Extract UniProt IDs (accession numbers)
        uniprot_ids = []
        for entry in root.findall('{http://uniprot.org/uniprot}entry'):  # Important namespace!
            accession_element = entry.find('{http://uniprot.org/uniprot}accession') # Important namespace!
            if accession_element is not None: # check if tag is found.
                uniprot_ids.append(accession_element.text)
        # print(uniprot_ids)
        return uniprot_ids

    except Exception as e:
        print(f"An error occurred: {e}")
        return []

def download_alphafold_structure(uniprot_id, output_dir="./alphafold_structures"):
    # Construct the AlphaFold database download URL
    # Note: Check the AlphaFold DB website for the most current URL structure.
    #       The URL format may change over time.  This is the format as of Oct 26, 2023
    url = f"https://alphafold.ebi.ac.uk/files/AF-{uniprot_id}-F1-model_v4.pdb"

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Construct the output file path
    output_file = os.path.join(output_dir, f"{uniprot_id}.pdb")

    if os.path.exists(output_file):
        print(f"Successfully downloaded AlphaFold structure for {uniprot_id} to {output_file}")
        return output_file

    try:
        # Make the request to the AlphaFold database
        response = requests.get(url, stream=True)  # Stream to handle potentially large files
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)

        # Save the structure to the output file
        with open(output_file, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):  # Write in chunks
                f.write(chunk)

        print(f"Successfully downloaded AlphaFold structure for {uniprot_id} to {output_file}")
        return output_file

    except requests.exceptions.HTTPError as e:
        print(f"Error downloading AlphaFold structure for {uniprot_id}: {e}")
        return None
    except requests.exceptions.RequestException as e:  # Catch more general request errors
        print(f"Error during request for {uniprot_id}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
def get_structure_based_on_name_ttd(protein_name):

    # get uniprot id based on name
    uniprot_name = get_uniprot_name_ttd(protein_name)
    print(uniprot_name)
    uniprot_id = map_uniprot_id_ttd(uniprot_name)
    print(uniprot_id)

    # get pdb structure based on uniprot id 
    pdb_id = get_pdb_id(uniprot_id)
    print(pdb_id)

    if not os.path.exists(f'{pdb_id}.pdb'):
        os.system(f'wget https://files.rcsb.org/download/{pdb_id}.pdb')

    # get alphafold-db structure based on uniprot id 

    return

def is_protein_name(protein_string, base_url, api_key):
    client = OpenAI(base_url=base_url,
                api_key=api_key)
    messages = [{"role": "system", "content": "You are an expert in bioinformatics."}]
    prompt = '''Let's think step by step. What is <pname></pname>. Is it a name of protein target ? You should ends with "My answer is : Yes/No."  If it is a cell line, a mutated protein, or not a standard protein name, you should answer No.'''
    
    prompt = prompt.replace('<pname></pname>', protein_string)
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        messages=messages,
        model="gemini-2.0-flash",
        temperature=0,
        # response_format={"type": "json_object"}
    )
    output = response.choices[0].message.content

    output = output.strip()
    if output.endswith('Yes') or output.endswith('Yes.'):
        return True
    elif output.endswith('No') or output.endswith('No.'):
        return False
    else:
        # print(output)
        return False
    
def protein_name_to_structure(protein_name, is_protein_name):
    if not is_protein_name:
        return None
    
    try:
        pdbs = query_pdb_by_protein_name(protein_name)
        if len(pdbs) > 0:
            pdb_structure_file = pdb_structure_based_on_pdb(pdbs[0])
            if pdb_structure_file is not None:
                # print(f'download pdb structure for {protein_name}, the structure is saved to {pdb_structure_file}')
                return pdb_structure_file
            
        uniprot_ids = query_uniprot_id_by_protein_name(protein_name)
        if len(uniprot_ids) == 0:
            # print(f'failed to find a structrure for {protein_name}')
            return None
        pdb_structure_file = pdb_structure_based_on_uniprot_id(uniprot_ids[0])
        if pdb_structure_file is not None:
            # print(f'download pdb structure for {protein_name}, the structure is saved to {pdb_structure_file}')
            return pdb_structure_file
        
        alphafold_structure_file = download_alphafold_structure(uniprot_ids[0])
        # print(f'download alphafold structure for {protein_name}, the structure is saved to {alphafold_structure_file}')
        return alphafold_structure_file
    
    except Exception as e:
        print(e)
        print(f'download protein structure failed for protein name {protein_name}')
        return None

if __name__ == '__main__':

    get_structure_based_on_name_ttd("hDMT1")

