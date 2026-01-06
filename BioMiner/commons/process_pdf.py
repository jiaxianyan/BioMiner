import os
import PyPDF2
import pdf2image
import json
from PIL import Image, ImageDraw, ImageFont
import cv2
import io
import base64
import re
Image.MAX_IMAGE_PIXELS = 933120000

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

def pdf_load_text_and_image_inference(pdf_path, save_path):
    # load text, directly return
    name = os.path.basename(pdf_path).split('.')[0]
    reader = PyPDF2.PdfReader(pdf_path)
    whole_text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        whole_text += text

    # load images, save as individual files, return image paths
    images = pdf2image.convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(save_path, f'{name}_image_{i}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)

    return whole_text, image_paths

def pdf_load_text_and_image(name, pdf_path, save_path):
    # load text, directly return
    reader = PyPDF2.PdfReader(pdf_path)
    whole_text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        whole_text += text

    # load images, save as individual files, return image paths
    images = pdf2image.convert_from_path(pdf_path)
    image_paths = []
    for i, image in enumerate(images):
        image_path = os.path.join(save_path, f'{name}_image_{i}.png')
        image.save(image_path, 'PNG')
        image_paths.append(image_path)

    return whole_text, image_paths

def load_pdf_pages_contain_tables_and_figures(name, middle_json_data, pdf_path, save_path):
    if middle_json_data is None:
        return pdf_load_pypdf_images(name, pdf_path, save_path)

    os.makedirs(os.path.join(save_path, name), exist_ok=True)
    pdf_images = pdf2image.convert_from_path(pdf_path)
    image_paths = []

    mineru_mode = 'pipline'
    # if '_backend' in middle_json_data.keys() and middle_json_data['_backend'] == 'vlm':
    #     mineru_mode = 'vlm'

    for pdf_page_info in middle_json_data['pdf_info']:
        page_idx = int(pdf_page_info['page_idx'])

        page_contain_images = False

        if mineru_mode == 'vlm':
            image_blocks = []
            for block in pdf_page_info['para_blocks']:
                if block['type'] in ['table', 'image']:
                    image_blocks.append(block)
        else:
            image_blocks = pdf_page_info['tables'] + pdf_page_info['images']

        for image in image_blocks:
            bbox = image['bbox']
            if len(bbox) > 0:
                page_contain_images = True
                break

        if page_contain_images:
            image_path = os.path.join(save_path, name, f'{name}_image_ctimg_{page_idx}.png')
            pdf_images[page_idx].save(image_path, 'PNG')
            image_paths.append(image_path)

    return image_paths

def load_pdf_seged_tables_and_figures(name, middle_json_data, pdf_path, save_path):
    pdf_images = pdf2image.convert_from_path(pdf_path)
    image_paths = []

    for pdf_page_info in middle_json_data['pdf_info']:
        page_idx = int(pdf_page_info['page_idx'])

        page_contain_images = False
        for image in pdf_page_info['tables'] + pdf_page_info['images']:
            bbox = image['bbox']
            if len(bbox) > 0:
                page_contain_images = True
                break

        if not page_contain_images:
            continue

        page_w, page_h = pdf_page_info['page_size']

        page_table_bboxs, page_figure_bboxs = [], []
        figure_valid = True
        table_valid = True

        for image in pdf_page_info['tables']:
            bbox = image['bbox']
            blocks = image['blocks']
            if len(bbox) == 0:
                table_valid = False
                break
            
            block_bbox_list = []
            block_names = []
            for block in blocks:
                xmin, ymin, xmax, ymax = block['bbox']
                # x, y, w, h = xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h
                block_names.append(block['type'])
                block_bbox_list.append((xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h))

            if 'table_body' in block_names and 'table_caption' in block_names:
                x,y,w,h = get_segment_size(block_bbox_list)
                page_table_bboxs.append((x,y,w,h))
            else:
                table_valid = False
                break

        for image in pdf_page_info['images']:
            bbox = image['bbox']
            blocks = image['blocks']
            if len(bbox) == 0:
                figure_valid = False
                break
            
            block_bbox_list = []
            block_names = []

            for block in blocks:
                xmin, ymin, xmax, ymax = block['bbox']
                # x, y, w, h = xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h
                block_names.append(block['type'])
                block_bbox_list.append((xmin/page_w, ymin/page_h, (xmax - xmin)/page_w, (ymax - ymin)/page_h))

            if 'image_body' in block_names and 'image_caption' in block_names:
                x,y,w,h = get_segment_size(block_bbox_list)
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
        if table_valid and figure_valid:
            if len(page_bbox) > 0:
                whole_image_path = os.path.join(save_path, f'{name}_image_ctimg_{page_idx}.png')
                page_img = pdf_images[page_idx]
                page_img.save(whole_image_path, 'PNG')

                for idx, bbox in enumerate(page_bbox):
                    seg_image_path = os.path.join(save_path, f'{name}_image_ctimg_{page_idx}_{idx}.png')
                    x, y, w, h = bbox
                    image_segment_given_box_xywh(whole_image_path, seg_image_path, x, y, w, h)
                    image_paths.append(seg_image_path)
        else:
            whole_image_path = os.path.join(save_path, f'{name}_image_ctimg_{page_idx}.png')
            page_img = pdf_images[page_idx]
            page_img.save(whole_image_path, 'PNG')
            image_paths.append(whole_image_path)
    return image_paths

def load_pdf_tables_and_figures_mineru(name, middle_json_data, pdf_path, save_path, seg_table_figure=False):
    if seg_table_figure:
        return load_pdf_seged_tables_and_figures(name, middle_json_data, pdf_path, save_path)
    else:
        return load_pdf_pages_contain_tables_and_figures(name, middle_json_data, pdf_path, save_path)


def pdf_load_mineru_text_and_images(name, miner_u_md_path, miner_u_middile_json_path, pdf_path, save_path, seg_table_figure):
    with open(miner_u_md_path, 'r') as f:
        whole_text = f.read()

    with open(miner_u_middile_json_path, 'r') as f:
        layout_middile_json = json.load(f)

    image_paths = load_pdf_tables_and_figures_mineru(name, layout_middile_json, pdf_path, save_path, seg_table_figure)

    return whole_text, image_paths

def pdf_load_pypdf_text(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    whole_text = ''
    for page_num in range(len(reader.pages)):
        page = reader.pages[page_num]
        text = page.extract_text()
        whole_text += text

    return whole_text

def pdf_load_mineru_text(miner_u_md_path, no_text_table):
    with open(miner_u_md_path, 'r') as f:
        whole_text = f.read()
    
    if no_text_table:
        whole_text = remove_tables_from_html(whole_text)

    return whole_text

def remove_tables_from_html(html_string):
    pattern = r"<html[^>]*>.*?</html>"  # Regex to match <table> tags and their contents
    return re.sub(pattern, "", html_string, flags=re.DOTALL | re.IGNORECASE)

def pdf_load_pypdf_images(name, pdf_path, save_path):
    # load images, save as individual files, return image paths

    os.makedirs(os.path.join(save_path, name), exist_ok=True)
    image_paths = []
    try:
        images = pdf2image.convert_from_path(pdf_path)
    except:
        return image_paths
    
    for i, image in enumerate(images):
        image_path = os.path.join(save_path, name, f'{name}_image_{i}.png')
        # if not os.path.exists(image_path):
        image.save(image_path, 'PNG')
        image_paths.append(image_path)

    return image_paths

def pdf_load_text_and_image_new(name, pdf_path, save_path, parse_txt_method, parse_image_method, no_text_table, miner_u_dir=None, miner_u_model='auto'):
    
    # print(save_path)
    if parse_txt_method == 'pypdf':
        whole_text = pdf_load_pypdf_text(pdf_path)
    elif parse_txt_method == 'mineru':
        miner_u_md_path = os.path.join(miner_u_dir, name, miner_u_model, f'{name}.md')
        if os.path.exists(miner_u_md_path):
            whole_text = pdf_load_mineru_text(miner_u_md_path, no_text_table)
        else:
            whole_text = pdf_load_pypdf_text(pdf_path)
    else:
        raise ValueError(f'Invalid text parse method: {parse_txt_method}')
    
    if parse_image_method == 'pypdf':
        image_paths = pdf_load_pypdf_images(name, pdf_path, save_path)
    elif parse_image_method == 'mineru_seg':
        miner_u_middile_json_path = os.path.join(miner_u_dir, name, miner_u_model, f'{name}_middle.json')
        if os.path.exists(miner_u_middile_json_path):
            with open(miner_u_middile_json_path, 'r') as f:
                middle_json_data = json.load(f)
            image_paths =  load_pdf_seged_tables_and_figures(name, middle_json_data, pdf_path, save_path)
        else:
            image_paths = pdf_load_pypdf_images(name, pdf_path, save_path)
    elif parse_image_method == 'mineru_contain':
        miner_u_middile_json_path = os.path.join(miner_u_dir, name, miner_u_model, f'{name}_middle.json')
        if os.path.exists(miner_u_middile_json_path):
            with open(miner_u_middile_json_path, 'r') as f:
                middle_json_data = json.load(f)
            image_paths =  load_pdf_pages_contain_tables_and_figures(name, middle_json_data, pdf_path, save_path)
        else:
            image_paths = pdf_load_pypdf_images(name, pdf_path, save_path)
    else:
        raise ValueError(f'Invalid image parse method : {parse_image_method}')
    # input(image_paths)
    return whole_text, image_paths

def encode_image(image_path):
    # compress and encode images
    with Image.open(image_path) as img:
        original_width, original_height = img.size
        max_long_side = 2000
        target_width = 768
        scale = target_width / original_width
        new_height = int(original_height * scale)
        if new_height > max_long_side:
            scale = max_long_side / new_height
            new_width = int(original_width * scale)
        else:
            new_width = target_width
        img_resized = img.resize((new_width, new_height))
        byte_io = io.BytesIO()
        img_resized.save(byte_io, format='png')
        bytes_image = byte_io.getvalue()
        return base64.b64encode(bytes_image).decode('utf-8')


def image_segment_given_box_xywh(image_path, save_path, x, y, w, h):
    image_origin = cv2.imread(image_path)
    height, width = image_origin.shape[:2]
    x_start_pixel = int(x * width)
    x_end_pixel = int((x + w) * width)
    y_start_pixel = int (y * height)
    y_end_pixel = int( (y+ h) * height) 
    segmented_image = image_origin[y_start_pixel: y_end_pixel, x_start_pixel:x_end_pixel]
    cv2.imwrite(save_path, segmented_image)
    return save_path


def draw_bbox_xywh(image, x, y, w, h, index, bbox_background=True):
    draw = ImageDraw.Draw(image)
    width = image.width
    height = image.height
    top_left_x = float(x * width)
    top_left_y = float(y * height)
    bottom_right_x = float((x + w) * width)
    bottom_right_y = float((y + h)  * height)
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
    
    font = ImageFont.truetype(font='./BioMiner/commons/arial.ttf', size=25)
    if bbox_background:
        left, top, right, bottom = draw.textbbox(text_position, text, font=font)
        draw.rectangle((left-5, top-5, right+5, bottom+5), fill='white')
    draw.text(text_position, text, font=font, fill=text_color)
    
    return 

