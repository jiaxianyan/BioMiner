import os 
import json
from collections import defaultdict
from PIL import Image, ImageDraw, ImageFont
from BioMiner.commons.process_pdf import image_segment_given_box_xywh, draw_bbox_xywh
from BioMiner.MolScribe.molscribe import MolScribe
from rdkit import Chem
from tqdm import tqdm 
from BioMiner.commons.molglyph_utils import get_refactor, Translator
from BioMiner.MolScribe.molscribe import MolGlyph

def visualize_all_box(name, bboxes, page_image_dir, save_path):
    if len(bboxes) > 0:
        os.makedirs(os.path.join(save_path, name), exist_ok=True)
    page2bbox = defaultdict(list)
    all_segmented_box_paths = []
    
    for bbox in bboxes:
        index = bbox['index']
        bbox_line = bbox['bbox']
        page = bbox['page']

        page2bbox[page].append({'index': index, 'bbox': bbox_line})
        
        page_image_path = os.path.join(page_image_dir, name, f'{name}_image_{page}.png')
        segmented_box_image = os.path.join(save_path, name, f'{name}_image_merge_bbox_{page}-{index}.png')
        x, y, w, h = bbox_line[0], bbox_line[1], bbox_line[2], bbox_line[3]
        image_segment_given_box_xywh(page_image_path, segmented_box_image, x, y, w, h)
        all_segmented_box_paths.append(segmented_box_image)

    for page in page2bbox.keys():
        page_bboxs = page2bbox[page]
        page_image_path = os.path.join(page_image_dir, name, f'{name}_image_{page}.png')
        augmented_full_image_path = os.path.join(save_path, name, f'{name}_image_merge_all_bboxes_{page}.png')
        image = Image.open(page_image_path)

        for bbox in page_bboxs:
            index = bbox['index']
            x, y, w, h = bbox['bbox'][0], bbox['bbox'][1], bbox['bbox'][2], bbox['bbox'][3]
            draw_bbox_xywh(image, x, y, w, h, index)            

        image.save(augmented_full_image_path)

    return all_segmented_box_paths

def run_molscribe_batch(bboxes, image_paths, device):
    model = MolScribe('swin_base_transformer_best.pth', device)
    if len(image_paths) == 0:
        return []

    output = model.predict_image_files(image_paths, return_atoms_bonds=False, return_confidence=False)

    pred_smiles = []
    # print(bboxes)
    for idx, (pred_res_item, image_path) in tqdm(enumerate(zip(output, image_paths)), desc='ocsr predciting'):
        smiles = pred_res_item['smiles']
        pred_smiles.append(smiles)
        # print(f'{image_path}:{smiles}')
        bboxes[idx]['smiles'] = smiles
    # print(bboxes)

    return bboxes

def run_molglyph_batch(bboxes, image_paths, device):
    model = MolGlyph(f'BioMiner/MolScribe/ckpts/MolGlyph.pth', device)
    if len(image_paths) == 0:
        return []

    output = model.predict_image_files(image_paths, return_atoms_bonds=False, return_confidence=False)

    pred_smiles = []
    # print(bboxes)
    for idx, (s, image_path) in enumerate(zip(output, image_paths)):
        smiles = get_refactor(Translator.refactor(s))
        pred_smiles.append(smiles)
        # print(f'{image_path}:{smiles}')
        bboxes[idx]['smiles'] = smiles
    # print(bboxes)

    return bboxes

def load_ocsr_external_res(res_json_file):
    if not os.path.exists(res_json_file):
        return []
    
    with open(res_json_file, 'r') as f:
        molparser_pred = json.load(f)

    return molparser_pred

def determine_mol_type(smi):
    if smi is None:
        return 'invalid'
    
    try:
        mol = Chem.MolFromSmiles(smi)
    except:
        return 'invalid'
    if mol is None:
        return 'invalid'

    if '*' in smi:
        return 'part'

    return 'full'

def prepare_full_markush_process(name, bboxes, page_image_dir, save_path):
    if len(bboxes) == 0:
        return [], [], {}, {}
    
    os.makedirs(os.path.join(save_path, name), exist_ok=True)

    page2bbox = {'part': defaultdict(list),
                 'full': defaultdict(list),
                 'invalid': defaultdict(list)}
    
    image2bboxindex = defaultdict(dict)

    index_smiles_dict = {}
    augmented_full_image_paths, augmented_part_image_paths = [], []

    for bbox in bboxes:
        index = bbox['index']
        bbox_line = bbox['bbox']
        page = bbox['page']
        smi = bbox['smiles']
        
        mol_type = determine_mol_type(smi)

        page2bbox[mol_type][page].append({'index': index, 
                                          'bbox': bbox_line, 
                                          'smiles': smi
                                        })
        
        index_smiles_dict[str(index)] = smi

        # save segmented box image for molscribe structure recognition
        page_image_path = os.path.join(page_image_dir, name, f'{name}_image_{page}.png')
        segmented_box_image = os.path.join(save_path, name, f'{name}_image_merge_bbox_{page}-{index}.png')
        x, y, w, h = bbox_line[0], bbox_line[1], bbox_line[2], bbox_line[3]
        image_segment_given_box_xywh(page_image_path, segmented_box_image, x, y, w, h)

    for page in page2bbox['full'].keys():
        page_bboxs = page2bbox['full'][page]
        page_image_path = os.path.join(page_image_dir, name, f'{name}_image_{page}.png')
        augmented_full_image_file_name = f'{name}_image_merge_full_{page}.png'
        augmented_full_image_path = os.path.join(save_path, name, augmented_full_image_file_name)
        image = Image.open(page_image_path)

        for bbox in page_bboxs:
            index = bbox['index']
            smi = bbox['smiles']
            x, y, w, h = bbox['bbox'][0], bbox['bbox'][1], bbox['bbox'][2], bbox['bbox'][3]
            draw_bbox_xywh(image, x, y, w, h, index)   
            image2bboxindex[augmented_full_image_file_name][index] = (x,y,w,h,page_image_path)  

        image.save(augmented_full_image_path)
        augmented_full_image_paths.append(augmented_full_image_path)
        


    for page in page2bbox['part'].keys():
        page_bboxs = page2bbox['part'][page]
        page_image_path = os.path.join(page_image_dir, name, f'{name}_image_{page}.png')
        augmented_part_image_file_name = f'{name}_image_merge_part_{page}.png'
        augmented_part_image_path = os.path.join(save_path, name, augmented_part_image_file_name)
        image = Image.open(page_image_path)

        for bbox in page_bboxs:
            index = bbox['index']
            smi = bbox['smiles']
            x, y, w, h = bbox['bbox'][0], bbox['bbox'][1], bbox['bbox'][2], bbox['bbox'][3]
            draw_bbox_xywh(image, x, y, w, h, index)
            image2bboxindex[augmented_part_image_file_name][index] = (x,y,w,h,page_image_path)

        image.save(augmented_part_image_path)
        augmented_part_image_paths.append(augmented_part_image_path)
        

    for page in page2bbox['invalid'].keys():
        page_bboxs = page2bbox['invalid'][page]
        page_image_path = os.path.join(page_image_dir, name, f'{name}_image_{page}.png')
        augmented_invalid_image_file_name = f'{name}_image_merge_invalid_{page}.png'
        augmented_invalid_image_path = os.path.join(save_path, name, augmented_invalid_image_file_name)
        image = Image.open(page_image_path)

        for bbox in page_bboxs:
            index = bbox['index']
            smi = bbox['smiles']
            x, y, w, h = bbox['bbox'][0], bbox['bbox'][1], bbox['bbox'][2], bbox['bbox'][3]
            draw_bbox_xywh(image, x, y, w, h, index)
            image2bboxindex[augmented_invalid_image_file_name][index] = (x,y,w,h,page_image_path)

        image.save(augmented_invalid_image_path)

    return augmented_full_image_paths, augmented_part_image_paths, index_smiles_dict, image2bboxindex