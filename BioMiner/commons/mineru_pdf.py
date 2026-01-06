import os
import torch
import shutil
import base64
import filetype
import tempfile
import fitz
import json
from pathlib import Path
from fastapi import HTTPException
from collections import defaultdict
import PyPDF2
import requests

try:
    from magic_pdf.tools.cli import do_parse, convert_file_to_pdf
    from magic_pdf.model.doc_analyze_by_custom_model import ModelSingleton
except:
    print(f'MinerU is not installed in this environment')
    
def check_bbox_in_area(bbox, area_bbox):
    # print(area_bbox)
    x, y, w, h = bbox
    a_x, a_y, a_w, a_h = area_bbox

    xmin = x
    ymin = y
    xmax = x + w
    ymax = y + h
    a_xmin = a_x
    a_ymin = a_y
    a_xmax = a_x + a_w
    a_ymax = a_y + a_h

    if xmin >= a_xmin and xmax<=a_xmax and ymin>=a_ymin and ymax <= a_ymax:
        return True
    else:
        return False
    
def get_segment_size(bbox_list, enlarge_size = 1/16):

    xmin_list, ymin_list, xmax_list, ymax_list = [], [], [], []
    for bbox in bbox_list:
        x, y, w, h = bbox
        xmin_list.append(x)
        ymin_list.append(y)
        xmax_list.append(x+w)
        ymax_list.append(y+h)

    xmin, ymin, xmax, ymax = min(xmin_list), min(ymin_list), max(xmax_list), max(ymax_list)
    xmin_enlarge = max(xmin - enlarge_size, 0)
    ymin_enlarge = max(ymin - enlarge_size, 0)
    xmax_enlarge = min(xmax + enlarge_size, 1)
    ymax_enlarge = min(ymax + enlarge_size, 1)

    new_x = xmin_enlarge
    new_y = ymin_enlarge
    new_w = xmax_enlarge - xmin_enlarge
    new_h = ymax_enlarge - ymin_enlarge
    return new_x, new_y, new_w, new_h

def load_model(device):
    if device.startswith('cuda'):
        os.environ['CUDA_VISIBLE_DEVICES'] = device.split(':')[-1]
        if torch.cuda.device_count() > 1:
            raise RuntimeError("Remove any CUDA actions before setting 'CUDA_VISIBLE_DEVICES'.")
    
    model_manager = ModelSingleton()
    model_manager.get_model(True, False)
    model_manager.get_model(False, False)
    print(f'MinerU Model initialization complete on device {device}!')

def cvt2pdf(file_base64):
    try:
        temp_dir = Path(tempfile.mkdtemp())
        temp_file = temp_dir.joinpath('tmpfile')
        file_bytes = base64.b64decode(file_base64)
        file_ext = filetype.guess_extension(file_bytes)

        if file_ext in ['pdf', 'jpg', 'png', 'doc', 'docx', 'ppt', 'pptx']:
            if file_ext == 'pdf':
                return file_bytes
            elif file_ext in ['jpg', 'png']:
                with fitz.open(stream=file_bytes, filetype=file_ext) as f:
                    return f.convert_to_pdf()
            else:
                temp_file.write_bytes(file_bytes)
                convert_file_to_pdf(temp_file, temp_dir)
                return temp_file.with_suffix('.pdf').read_bytes()
        else:
            raise Exception('Unsupported file format')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

def to_b64(file_path):
    try:
        with open(file_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        raise Exception(f'File: {file_path} - Info: {e}')

def pdf_load_pypdf_text(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    whole_text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        whole_text += text

    return whole_text

def run_mineru(file_name, file_path, output_dir, device, mineru_mode='auto'):
    # mineru_mode: auto or vlm
    mineru_layout_file = os.path.join(output_dir, file_name, f'{mineru_mode}/{file_name}_middle.json')
    
    if not os.path.exists(mineru_layout_file):
        load_model(device)
        file = to_b64(file_path)
        # file_name = os.path.basename(file_path).split('.')[0]
        file = cvt2pdf(file)
        opts = {}
        opts.setdefault('debug_able', False)
        opts.setdefault('parse_method', mineru_mode)
        try:
            do_parse(output_dir, file_name, file, [], **opts)
        except:
            print(f'run mineru for {file_name} failed')

    if os.path.exists(mineru_layout_file):
        with open(mineru_layout_file, 'r') as f:
            mineru_layout = json.load(f)

        mineru_text_file = os.path.join(output_dir, file_name, f'{mineru_mode}/{file_name}.md')

        with open(mineru_text_file, 'r') as f:
            mineru_text = f.read()
    else:
        mineru_layout = None
        try:
            mineru_text = pdf_load_pypdf_text(file_path)
        except:
            mineru_text = ''

    return mineru_layout, mineru_text

def run_mineru_client_step(input_batch, url='http://127.0.0.1:8002/predict'):

    file_name, file_path, output_dir = input_batch

    mineru_layout_file = os.path.join(output_dir, file_name, f'auto/{file_name}_middle.json')

    try:
        response = requests.post(url, json={
            'file': to_b64(file_path),
            'file_name': file_name,
            'output_dir': output_dir
        })

        if response.status_code != 200:
            print(f'File: {file_path} - Info: failed')

    except Exception as e:
        print(f'File: {file_path} - Info: {e}')

    if os.path.exists(mineru_layout_file):
        with open(mineru_layout_file, 'r') as f:
            mineru_layout = json.load(f)

        mineru_text_file = os.path.join(output_dir, file_name, f'auto/{file_name}.md')

        with open(mineru_text_file, 'r') as f:
            mineru_text = f.read()
    else:
        mineru_layout = None
        try:
            mineru_text = pdf_load_pypdf_text(file_path)
        except:
            mineru_text = ''

    return mineru_layout, mineru_text


def run_mineru_client(names, pdf_paths, output_dir, grounding_gpu_num):

    import numpy as np
    from joblib import Parallel, delayed

    batches = []
    for n, p, o in zip(names, pdf_paths, [output_dir]*len(names)):
        batches.append((n, p, o))

    n_jobs = np.clip(len(batches), 1, grounding_gpu_num)

    results = Parallel(n_jobs, prefer='threads', verbose=10)(
        delayed(run_mineru_client_step)(b) for b in batches
    )

    mineru_layouts, mineru_texts = [], []
    for res in results:
        mineru_layouts.append(res[0])
        mineru_texts.append(res[1])

    return mineru_layouts, mineru_texts

def get_mineru_table_body_bbox(mineru_layout, enlarge_size = 0.0):
    minuer_table_bbox_dict = defaultdict(list)
    
    mineru_mode = 'auto'
    # if '_backend' in mineru_layout.keys() and mineru_layout['_backend'] == 'vlm':
    #     mineru_mode = 'vlm'

    for pdf_page_info in mineru_layout['pdf_info']:
        page_idx = pdf_page_info['page_idx']
        page_w, page_h = pdf_page_info['page_size']
        page_table_bboxs = []

        if mineru_mode == 'vlm':
            table_blocks = []
            for block in pdf_page_info['para_blocks']:
                if block['type'] == 'table':
                    table_blocks.append(block)
        else: 
            table_blocks = pdf_page_info['tables']
        

        for image in table_blocks:
            bbox = image['bbox']
            if len(bbox) == 0:
                continue
            xmin, ymin, xmax, ymax = bbox
            enlarge_bbox = get_segment_size([(xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h)], enlarge_size=enlarge_size)
            page_table_bboxs.append(enlarge_bbox)
            
        if len(page_table_bboxs) > 0:
            minuer_table_bbox_dict[page_idx] = page_table_bboxs

    return minuer_table_bbox_dict

def get_mineru_complete_figure_table_bbox(mineru_layout, enlarge_size = 1/32):
    minuer_figure_table_bbox_dict = defaultdict(list)

    mineru_mode = 'auto'
    # if '_backend' in mineru_layout.keys() and mineru_layout['_backend'] == 'vlm':
    #     mineru_mode = 'vlm'

    for pdf_page_info in mineru_layout['pdf_info']:
        page_idx = pdf_page_info['page_idx']
        page_w, page_h = pdf_page_info['page_size']
        page_table_bboxs, page_figure_bboxs = [], []

        figure_valid = True
        table_valid = True

        if mineru_mode == 'vlm':
            table_blocks = []
            image_blocks = []
            for block in pdf_page_info['para_blocks']:
                if block['type'] == 'table':
                    table_blocks.append(block)
                elif block['type'] == 'image':
                    image_blocks.append(block)
        else:
            table_blocks = pdf_page_info['tables']
            image_blocks = pdf_page_info['images']

        for image in table_blocks:
            bbox = image['bbox']
            blocks = image['blocks']
            if len(bbox) == 0:
                table_valid = False
                break
            
            block_bbox_list = []
            block_names = []
            for block in blocks:
                xmin, ymin, xmax, ymax = block['bbox']
                block_names.append(block['type'])
                block_bbox_list.append((xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h))

            if 'table_body' in block_names and 'table_caption' in block_names:
                x,y,w,h = get_segment_size(block_bbox_list, enlarge_size=enlarge_size)
                page_table_bboxs.append((x,y,w,h))
            else:
                table_valid = False
                break

        for image in image_blocks:
            bbox = image['bbox']
            blocks = image['blocks']
            if len(bbox) == 0:
                figure_valid = False
                break
            
            block_bbox_list = []
            block_names = []

            for block in blocks:
                xmin, ymin, xmax, ymax = block['bbox']
                block_names.append(block['type'])
                block_bbox_list.append((xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h))

            if 'image_body' in block_names and 'image_caption' in block_names:
                x,y,w,h = get_segment_size(block_bbox_list, enlarge_size=enlarge_size)
                page_figure_bboxs.append((x,y,w,h))
            elif 'image_body' in block_names:
                figure_in_table_flag = False
                for table_bbox in page_table_bboxs:
                    if check_bbox_in_area((xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h), table_bbox):
                        figure_in_table_flag = True
                        break
                if not figure_in_table_flag:
                    figure_valid = False
            else:
                figure_valid = False
                break
        
        page_bbox = page_table_bboxs + page_figure_bboxs 
        if not table_valid or not figure_valid:
            # print(f'error page {page_idx}')
            s = f'error page {page_idx}'
        else:
            if len(page_bbox) > 0:
                minuer_figure_table_bbox_dict[page_idx] = page_bbox

    return minuer_figure_table_bbox_dict
