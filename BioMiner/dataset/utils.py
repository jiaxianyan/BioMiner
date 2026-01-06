import os

prompt_dict = {'gpt-4o':'gpt-series-prompt',
               'gpt-4o-mini':'gpt-series-prompt',
               'gpt-4.1-mini':'gpt-series-prompt'}

structure_prompt_strategy = {'origin': '',
                             'origin-with-box-index': '_with_index',
                             'updated-with-box-index': '_updated_with_index',
                             'updated-v3-with-box-index': '_updated_v3_with_index'
                             }


bioactivity_prompt_strategy = {'origin': '',
                                'updated': '_updated',
                                'updated_v3': '_updated_v3'
                                }


def load_prompts(prompt_path='BioMiner/commons/prompts', 
                 text_mllm='local-biominer-instruct', 
                 vision_mllm='local-biominer-instruct', 
                 bioactivity_text_strategy='updated', 
                 bioactivity_image_strategy='updated', 
                 structure_full_strategy='updated-with-box-index', 
                 structure_part_strategy='updated-with-box-index'):
    bioactivity_text_prompt_path = os.path.join(prompt_path, prompt_dict.get(text_mllm, 'gemini-series-prompt'), f'prompt_for_text{bioactivity_prompt_strategy[bioactivity_text_strategy]}.txt')
    bioactivity_image_prompt_path = os.path.join(prompt_path, prompt_dict.get(vision_mllm, 'gemini-series-prompt'), f'prompt_for_image{bioactivity_prompt_strategy[bioactivity_image_strategy]}.txt')
    structure_full_prompt_path = os.path.join(prompt_path, prompt_dict.get(vision_mllm, 'gemini-series-prompt'), f'prompt_for_structure_full{structure_prompt_strategy[structure_full_strategy]}.txt')
    structure_part_prompt_path = os.path.join(prompt_path, prompt_dict.get(vision_mllm, 'gemini-series-prompt'), f'prompt_for_structure_part{structure_prompt_strategy[structure_part_strategy]}.txt')
    merge_prompt_path = os.path.join(prompt_path, prompt_dict.get(text_mllm, 'gemini-series-prompt'), 'prompt_for_merging_without_ligand_structure.txt')

    with open(bioactivity_text_prompt_path, 'r') as f:
        bioactivity_text_prompt = f.read().strip()

    with open(bioactivity_image_prompt_path, 'r') as f:
        bioactivity_image_prompt = f.read().strip()

    with open(structure_full_prompt_path, 'r') as f:
        structure_full_prompt = f.read().strip()

    with open(structure_part_prompt_path, 'r') as f:
        structure_part_prompt = f.read().strip()

    with open(merge_prompt_path, 'r') as f:
        merge_prompt = f.read().strip()

    return bioactivity_text_prompt, bioactivity_image_prompt, structure_full_prompt, structure_part_prompt, merge_prompt
