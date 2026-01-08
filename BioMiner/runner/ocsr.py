import os
import json
import re
import torch
import cv2
from PIL import Image, ImageDraw, ImageFont
# from molscribe import MolScribe
# from rxnscribe import MolDetect
from huggingface_hub import hf_hub_download

def draw_bbox(parsed_path, file_name):
    bbox_path = os.path.join(parsed_path, f'{file_name}_bbox.json')
    with open(bbox_path, 'r', encoding='utf-8') as file:
        bboxes = json.load(file)
    full_bbox_image_names = []
    part_bbox_image_names = []
    for bbox in bboxes:
        index = bbox['index']
        bbox_line = bbox['bbox']
        page = bbox['page']

        if bbox['type'] == 'full':
            full_bbox_image_path = os.path.join(parsed_path, f'{file_name}_image_bbox_full_{page}.png')

            if not os.path.exists(full_bbox_image_path):
                origin_image_path = os.path.join(parsed_path, f'{file_name}_image_{page}.png')
                image = Image.open(origin_image_path)
                image.save(full_bbox_image_path)

            image = Image.open(full_bbox_image_path)

        else:
            part_bbox_image_path = os.path.join(parsed_path, f'{file_name}_image_bbox_part_{page}.png')

            if not os.path.exists(part_bbox_image_path):
                origin_image_path = os.path.join(parsed_path, f'{file_name}_image_{page}.png')
                image = Image.open(origin_image_path)
                image.save(part_bbox_image_path)

            image = Image.open(part_bbox_image_path)

        draw = ImageDraw.Draw(image)
        normalized_coords = bbox_line
        width = image.width
        height = image.height
        top_left_x = float(normalized_coords[1] * width)
        top_left_y = float(normalized_coords[0] * height)
        bottom_right_x = float(normalized_coords[3] * width)
        bottom_right_y = float(normalized_coords[2] * height)
        top_left = (top_left_x, top_left_y)
        bottom_right = (bottom_right_x, bottom_right_y)
        top_right = (bottom_right_x, top_left_y)
        bottom_left = (top_left_x, bottom_right_y)
        line_width = 2
        line_color = (255, 0, 0)
        draw.line([top_left, top_right], fill=line_color, width=line_width)
        draw.line([top_right, bottom_right], fill=line_color, width=line_width)
        draw.line([bottom_right, bottom_left], fill=line_color, width=line_width)
        draw.line([bottom_left, top_left], fill=line_color, width=line_width)

        text = str(index)
        text_color = (255, 0, 0)
        text_position = ((top_left_x, top_left_y))
       
        font = ImageFont.truetype(font='./BioMiner/arial.ttf', size=25)
        draw.text(text_position, text, font=font, fill=text_color)
        if bbox['type'] == 'full':
            image.save(full_bbox_image_path)
            if f'{file_name}_image_bbox_full_{page}.png' not in full_bbox_image_names:
                full_bbox_image_names.append(f'{file_name}_image_bbox_full_{page}.png')
        else:
            image.save(part_bbox_image_path)
            if f'{file_name}_image_bbox_part_{page}.png' not in part_bbox_image_names:
                part_bbox_image_names.append(f'{file_name}_image_bbox_part_{page}.png')
    with open(os.path.join(parsed_path, f'{file_name}_parsed.json'), 'r') as f:
        parsed = json.load(f)
    parsed['full_bbox_image'] = full_bbox_image_names
    parsed['part_bbox_image'] = part_bbox_image_names
    with open(os.path.join(parsed_path, f'{file_name}_parsed.json'), 'w') as f:
        json.dump(parsed, f)

def segment_openchemie(parsed_path, file_basename):
    bbox_files = []
    ckpt_path = hf_hub_download("Ozymandias314/MolDetectCkpt", "coref_best_hf.ckpt")
    model = MolDetect(ckpt_path, device=torch.device('cuda'), coref = True)  
    with open(os.path.join(parsed_path, f'{file_basename}_parsed.json'), 'r') as f:
        parsed = json.load(f)
    for image_name in image_names:
        index = 0
        image_base_name, _ = os.path.splitext(image_name)
        # print(image_name)
        path = os.path.join(parsed_path, image_name)
        predictions = model.predict_image_file(path, coref = True)
        bboxes = predictions['bboxes']
        bbox_file_name= f"{image_base_name}_bbox.json"
        bbox_file = []
        image_origin = cv2.imread(path)
        height, width = image_origin.shape[:2]
        for bbox in bboxes:
            if bbox['category_id'] == 1:
                image = f'{image_base_name}_{index}.png'
                bbox_ = [bbox['bbox'][1], bbox['bbox'][0], bbox['bbox'][3], bbox['bbox'][2]]
                segmented_image = image_origin[int(bbox_[0]*height):int(bbox_[2]*height), int(bbox_[1]*width):int(bbox_[3]*width)]
                cv2.imwrite(os.path.join(parsed_path, image), segmented_image)
                bbox_file.append(
                    {
                        'image': image,
                        'bbox': bbox_
                    }
                )
                index = index + 1
        with open(os.path.join(parsed_path, bbox_file_name), 'w') as f:
            json.dump(bbox_file, f)
        bbox_files.append(bbox_file_name)
    parsed['bbox'] = bbox_files
    with open(os.path.join(parsed_path, f'{file_basename}_parsed.json'), 'w') as f:
        json.dump(parsed, f)


def pre_process_smiles(in_smiles):
    count = 0
    def replacer(match):
        nonlocal count
        count += 1
        return f"[*:{count}]"
    pattern = r"\*|\[\*\]|\[\*\d+\]" 
    out_smiles = re.sub(pattern, replacer, in_smiles)
    return out_smiles


def ocsr(parsed_path, file_name):

    ckpt_path = './swin_base_char_aux_1m.pth'
    molscribe = MolScribe(ckpt_path, device=torch.device('cuda:0'))

    with open(os.path.join(parsed_path, f'{file_name}_parsed.json'), 'r') as f:
        parsed = json.load(f)
    bbox_files = parsed['bbox']
    # ckpt_path = hf_hub_download('yujieq/MolScribe', 'swin_base_char_aux_1m.pth')
    index = 0
    data = []
    for bbox_file in bbox_files:
        page_number = bbox_file.split("_")[-2]
        with open(os.path.join(parsed_path, bbox_file), 'r', encoding='utf-8') as file:
            page_data = json.load(file)
        for bbox_image in page_data:
            try:
                image_name = bbox_image['image']
                # print(image_name)
                bbox = bbox_image['bbox']
                output = molscribe.predict_image_file(os.path.join(parsed_path, image_name), return_atoms_bonds=True, return_confidence=True)
                smiles = output['smiles']
                if '*' in smiles:
                    type_ = "part"
                    smiles = pre_process_smiles(smiles)
                else:
                    type_ = "full"
                pair = { "index": index, "page": page_number, "smiles": smiles, "bbox": bbox, "type": type_ }
                # print(pair)
                index = index + 1
                data.append(pair)
            except:
                continue
        # print(data)
    with open(os.path.join(parsed_path, f'{file_name}_bbox.json'), 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


        