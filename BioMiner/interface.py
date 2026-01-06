import warnings
warnings.filterwarnings("ignore")
import os
import pickle
import json
from collections import defaultdict
from tqdm import tqdm
from BioMiner.commons.utils import pmap_multi
from BioMiner.commons.process_pdf import pdf_load_pypdf_images, image_segment_given_box_xywh, load_pdf_pages_contain_tables_and_figures
from BioMiner.commons.mineru_pdf import run_mineru_client, get_mineru_table_body_bbox, get_mineru_complete_figure_table_bbox
from BioMiner.commons.mol_detection import merge_full_page_and_seg_table_bbox, run_yolo_batch_global_client
from BioMiner.commons.ocsr import visualize_all_box, prepare_full_markush_process, run_molglyph_batch
from BioMiner.dataset.utils import load_prompts, bioactivity_prompt_strategy, structure_prompt_strategy
from BioMiner.runner.extractor import extraction_ligand_structure_step, extraction_bioactivity_step, save_overall_result, extract_markush_part_with_bbox_index_split_complex_image_seg_layout
from BioMiner.runner.mllm import get_api_client
from BioMiner.runner.metric_fn import resulter, evaluate_step
from BioMiner.commons.molglyph_utils import get_refactor, Translator, get_new_smiles
from BioMiner.MolScribe.molscribe import MolGlyph
from joblib import Parallel, delayed
import requests
import numpy as np
from loguru import logger

def process_single_pdf_chemical_structure_mllm(
    name, bboxes_with_pred_smiles, mineru_complete_figure_table_bbox,
    page_image_path, augment_full_markush_path, extraction_result_path, vision_mllm_type, base_url, api_key,
    structure_full_prompt, structure_part_prompt, structure_full_suffix, structure_part_suffix,
    structure_cot, split_bbox_num, segment_image, enlarge_size,
    structure_full_layout_seg, structure_part_layout_seg, bbox_background,
    overwrite_structure_full, overwrite_structure_part
):
    augmented_full_image_paths, augmented_part_image_paths, index_smiles_dict, image2bboxindex = prepare_full_markush_process(name, bboxes_with_pred_smiles, page_image_path, augment_full_markush_path)

    vision_mllm_client = get_api_client(vision_mllm_type, base_url, api_key)

    pdf_augmented_full_image_bbox_index_dict=[image2bboxindex[os.path.basename(image_path)] for image_path in augmented_full_image_paths]
    pdf_augmented_part_image_bbox_index_dict=[image2bboxindex[os.path.basename(image_path)] for image_path in augmented_part_image_paths]

    # print(mineru_complete_figure_table_bbox)
    full_page_figure_table_layout_bbox, part_page_figure_table_layout_bbox = [], []
    for image_path in augmented_full_image_paths:
        file_name = os.path.basename(image_path)
        file_name_items = file_name.split('.')[0].split('_')
        page_idx = int(file_name_items[-1])
        try:
            full_page_figure_table_layout_bbox.append(mineru_complete_figure_table_bbox[page_idx])
        except:
            full_page_figure_table_layout_bbox.append(None)

    for image_path in augmented_part_image_paths:
        file_name = os.path.basename(image_path)
        file_name_items = file_name.split('.')[0].split('_')
        page_idx = int(file_name_items[-1])
    
        try:
            part_page_figure_table_layout_bbox.append(mineru_complete_figure_table_bbox[page_idx])
        except:
            part_page_figure_table_layout_bbox.append(None)

    os.makedirs(os.path.join(extraction_result_path, name), exist_ok=True)
    structure_data_list = extraction_ligand_structure_step(name, 
                                                            vision_mllm_type, 
                                                            vision_mllm_client,
                                                            augmented_full_image_paths,
                                                            augmented_part_image_paths, 
                                                            index_smiles_dict, 
                                                            pdf_augmented_full_image_bbox_index_dict,
                                                            pdf_augmented_part_image_bbox_index_dict, 
                                                            full_page_figure_table_layout_bbox, 
                                                            part_page_figure_table_layout_bbox,
                                                            structure_full_prompt, 
                                                            structure_part_prompt,
                                                            extraction_result_path,
                                                            structure_full_suffix,
                                                            structure_part_suffix,
                                                            structure_cot, 
                                                            split_bbox_num, 
                                                            segment_image, 
                                                            enlarge_size, 
                                                            structure_full_layout_seg, 
                                                            structure_part_layout_seg, 
                                                            bbox_background,
                                                            overwrite_structure_full, 
                                                            overwrite_structure_part)
            
    return structure_data_list


def process_single_bioactivity_measurement(
    name, pdf_text, pdf_image_paths,
    text_mllm_type, vision_mllm_type, base_url, api_key,
    bioactivity_text_prompt, bioactivity_image_prompt,
    merge_strategy, extraction_result_path,
    bioactivity_text_suffix, bioactivity_image_suffix,
    bioactivity_cot, overwrite_bioactivity_text, overwrite_bioactivity_image):

    text_mllm_client = get_api_client(text_mllm_type, base_url, api_key)
    vision_mllm_client = get_api_client(vision_mllm_type,base_url, api_key)

    os.makedirs(os.path.join(extraction_result_path, name), exist_ok=True)
    bioactivity_data_lists = extraction_bioactivity_step(name, 
                                                        text_mllm_type, 
                                                        text_mllm_client, 
                                                        vision_mllm_type,
                                                        vision_mllm_client,
                                                        pdf_text,
                                                        pdf_image_paths, 
                                                        bioactivity_text_prompt,
                                                        bioactivity_image_prompt, 
                                                        merge_strategy,
                                                        extraction_result_path, 
                                                        extraction_result_path,
                                                        bioactivity_text_suffix,
                                                        bioactivity_image_suffix,
                                                        bioactivity_cot,
                                                        overwrite_bioactivity_text,
                                                        overwrite_bioactivity_image)
            
    return bioactivity_data_lists

def process_mineru_single(name, mineru_layout, pdf_path, page_image_path):
    # try:
    if mineru_layout is None:
        table_body_bbox = {}
        complete_figure_table_bbox = {}
        pages_images_contain_tables_and_figures_paths = load_pdf_pages_contain_tables_and_figures(name, mineru_layout, pdf_path, page_image_path)
    else:
        table_body_bbox = get_mineru_table_body_bbox(mineru_layout)
        complete_figure_table_bbox = get_mineru_complete_figure_table_bbox(mineru_layout)
        pages_images_contain_tables_and_figures_paths = load_pdf_pages_contain_tables_and_figures(name, mineru_layout, pdf_path, page_image_path)
    # except:
    #     raise ValueError(f'{pdf_path} error')
    
    return table_body_bbox, complete_figure_table_bbox, pages_images_contain_tables_and_figures_paths


def worker_preprocess_doc(name, page_image_paths, mineru_table_body_bbox, 
                          page_image_root, full_page_save_dir, seg_table_save_dir):
    """
    Worker 1: 负责单篇文档的图片裁剪和路径整理
    """
    # 1. 准备全页图片路径
    doc_full_page_paths = []
    doc_full_page_save_paths = []
    
    for img_path in page_image_paths:
        doc_full_page_paths.append(img_path)
        save_path = os.path.join(full_page_save_dir, name, os.path.basename(img_path))
        doc_full_page_save_paths.append(save_path)

    # 2. 准备表格图片 (裁剪)
    doc_seg_table_paths = []
    doc_seg_table_save_paths = []
    doc_seg_layouts = [] # 记录裁剪图对应的原始 layout bbox
    doc_seg_pages = []   # 记录页码

    for page in mineru_table_body_bbox.keys():
        page_table_body_bboxs = mineru_table_body_bbox[page]
        origin_image_path = os.path.join(page_image_root, name, f'{name}_image_{page}.png')
        
        for bbox_idx, bbox in enumerate(page_table_body_bboxs):
            segmented_table_path = os.path.join(page_image_root, name, f'{name}_image_{page}_tb_{bbox_idx}.png')
            
            # --- IO 密集型操作: 裁剪图片 ---
            x, y, w, h = bbox
            image_segment_given_box_xywh(origin_image_path, segmented_table_path, x, y, w, h)
            # ---------------------------
            
            doc_seg_table_paths.append(segmented_table_path)
            save_path = os.path.join(seg_table_save_dir, name, os.path.basename(segmented_table_path))
            doc_seg_table_save_paths.append(save_path)
            doc_seg_layouts.append(bbox)
            doc_seg_pages.append(page)

    return {
        'full_paths': doc_full_page_paths,
        'full_save_paths': doc_full_page_save_paths,
        'seg_paths': doc_seg_table_paths,
        'seg_save_paths': doc_seg_table_save_paths,
        'seg_layouts': doc_seg_layouts,
        'seg_pages': doc_seg_pages
    }

def worker_postprocess_doc(name, full_page_bboxes, seg_table_bboxes, 
                           page_image_root, merge_detection_path):
    """
    Worker 2: 负责单篇文档的结果合并与可视化
    """
    # --- 逻辑密集型: 合并坐标 ---
    merge_pdf_bboxes = merge_full_page_and_seg_table_bbox(full_page_bboxes, seg_table_bboxes)
    
    # --- IO 密集型: 画图保存 ---
    all_segmented_box_paths = visualize_all_box(name, merge_pdf_bboxes, page_image_root, merge_detection_path)
    
    return merge_pdf_bboxes, all_segmented_box_paths


class BioMiner():
    def __init__(self, config, biovista_evaluate=False):
        self.init_biominer(config)
        if biovista_evaluate:
            self.init_biovista(config)
        self.biovista_evaluate = biovista_evaluate

    def init_pred_dir(self, pdf_paths):
        self.page_image_path = os.path.join(self.output_dir, 'page_images')
        self.mineru_path = os.path.join(self.output_dir, 'mineru')
        self.full_page_detection_path = os.path.join(self.output_dir, f'md_full_{self.mol_detection_model}')
        self.seg_table_detection_path = os.path.join(self.output_dir, f'md_part_{self.mol_detection_model}')
        self.merge_detection_path = os.path.join(self.output_dir, f'md_merge_{self.mol_detection_model}_yolo',)
        self.augment_full_markush_path = os.path.join(self.output_dir, f'md_merge_{self.mol_detection_model}_yolo_distinguish_full_markush_after_ocsr')
        self.extraction_result_path = os.path.join(self.output_dir, f'extraction_{self.text_mllm_type}')
        self.stage_one_result_path = os.path.join(self.output_dir, 'stage_one.pkl')
        self.stage_preprocess_result_path = os.path.join(self.output_dir, 'stage_preprocess.pkl')
        self.stage_proporcess_yolo_results = os.path.join(self.output_dir, 'stage_preprocess_yolo.pkl')


        names = []
        for pdf_path in pdf_paths:
            name = os.path.basename(pdf_path).split('.')[0]
            names.append(name)

        # names.sort()
        with open(f'{self.output_dir}/{self.task_name}.txt', 'w') as f:
            f.write('\n'.join(names))

        # input()

        return names

    def init_biominer(self, config):
        self.n_jobs = config.n_jobs
        self.output_dir = config.output_dir
        os.makedirs(self.output_dir, exist_ok=True)
        self.overwrite_structure_full = config.overwrite_structure_full
        self.overwrite_structure_part = config.overwrite_structure_part
        self.overwrite_bioactivity_text = config.overwrite_bioactivity_text
        self.overwrite_bioactivity_image = config.overwrite_bioactivity_image

        self.text_mllm_type = config.model.text_mllm_type
        self.vision_mllm_type = config.model.vision_mllm_type
        self.base_url = config.model.base_url
        self.api_key = config.model.api_key

        self.mol_detection_model = config.model.mol_detection_model
        self.ocsr_model = config.model.ocsr_model
        self.grounding_gpu_num = config.grounding_gpu_num

        self.structure_cot = config.model.structure_cot
        self.split_bbox_num = config.model.structure_full_split_molecule_num
        self.segment_image = config.model.structure_full_seg_image
        self.enlarge_size = config.model.structure_full_seg_enlarge
        self.structure_full_layout_seg = config.model.structure_full_layout_seg
        self.structure_part_layout_seg = config.model.structure_part_layout_seg
        self.bbox_background = config.model.structure_index_bbox_background
        self.merge_strategy = config.model.merge_strategy
        self.bioactivity_cot = config.model.bioactivity_cot

        bioactivity_text_prompt, bioactivity_image_prompt, structure_full_prompt, structure_part_prompt, merge_prompt = load_prompts(prompt_path='BioMiner/commons/prompts', 
                                                                                                                                     text_mllm=config.model.text_mllm_type, 
                                                                                                                                     vision_mllm=config.model.vision_mllm_type, 
                                                                                                                                     bioactivity_text_strategy=config.model.bioactivity_text_strategy, 
                                                                                                                                     bioactivity_image_strategy=config.model.bioactivity_image_strategy, 
                                                                                                                                     structure_full_strategy=config.model.structure_full_strategy, 
                                                                                                                                     structure_part_strategy=config.model.structure_part_strategy)
        self.bioactivity_text_prompt = bioactivity_text_prompt
        self.bioactivity_image_prompt = bioactivity_image_prompt
        self.structure_full_prompt = structure_full_prompt
        self.structure_part_prompt = structure_part_prompt
        self.merge_prompt = merge_prompt

        bioactivity_text_suffix = bioactivity_prompt_strategy[config.model.bioactivity_text_strategy]
        bioactivity_image_suffix = bioactivity_prompt_strategy[config.model.bioactivity_image_strategy]

        if config.data.parse_text_method == 'mineru':
            bioactivity_text_suffix += '_txtmu'
            if config.data.no_text_table:
                bioactivity_text_suffix += '_ntb'
        if config.data.parse_image_method == 'mineru_contain':
            bioactivity_image_suffix += '_imgmuc'
        elif config.data.parse_image_method == 'mineru_seg':
            bioactivity_image_suffix += '_imgmus'

        structure_full_suffix = f'{config.model.mol_detection_model}_bbox_{config.model.ocsr_model}_ocsr' + '_' + structure_prompt_strategy[config.model.structure_full_strategy]
        structure_part_suffix = f'{config.model.mol_detection_model}_bbox_{config.model.ocsr_model}_ocsr' + '_' + structure_prompt_strategy[config.model.structure_part_strategy]
        
        if config.model.structure_cot:
            structure_full_suffix += '_cot'
            structure_part_suffix += '_cot'
        
        if config.model.structure_full_split_molecule_num is not None:
            structure_full_suffix += f'_split{config.model.structure_full_split_molecule_num}'

        if config.model.structure_full_seg_image:
            structure_full_suffix += f'seg{config.model.structure_full_seg_enlarge}'
  
        if config.model.structure_index_bbox_background:
            structure_full_suffix += f'_bg'
            structure_part_suffix += f'_bg'

        if config.model.structure_full_layout_seg:
            structure_full_suffix += f'_lo'

        if config.model.structure_part_layout_seg:
            structure_part_suffix += f'_lo'

        self.structure_full_suffix = structure_full_suffix
        self.structure_part_suffix = structure_part_suffix
        self.bioactivity_text_suffix = bioactivity_text_suffix
        self.bioactivity_image_suffix = bioactivity_image_suffix

        self.task_name = config.task_name

        return 

    def init_biovista(self, config):
        self.top_n = config.test.top_n
        self.pdb_name_path = config.test.pdb_name_path
        self.pdb_label_path = config.test.pdb_label_path
        self.pdb_structure_path = config.test.pdb_structure_path
        self.labels_base_dir = config.test.labels_base_dir
        self.dataset_name = config.test.dataset_name

        return

    def agent_preprocess(self, names, pdf_paths):
        # mineru_layouts, mineru_texts = [], []

        # convert pdf pages to images
        page_image_pathss = pmap_multi(pdf_load_pypdf_images, 
                                      zip(names, pdf_paths),
                                      save_path=self.page_image_path,
                                      n_jobs=self.n_jobs,
                                      desc='converting pdf pages to images')
        
        # MinerU layout analysis and reading order determination
        # for name, pdf_path in tqdm(zip(names, pdf_paths), desc='run mineru'):
        #     mineru_layout, mineru_text = run_mineru(name, pdf_path, self.mineru_path)
        #     mineru_layouts.append(mineru_layout)
        #     mineru_texts.append(mineru_text)

        mineru_layouts, mineru_texts = run_mineru_client(names, pdf_paths, self.mineru_path, self.grounding_gpu_num)

        # process mineru layout
        res = pmap_multi(process_mineru_single,
                   zip(names, mineru_layouts, pdf_paths),
                   page_image_path=self.page_image_path,
                   n_jobs=self.n_jobs,
                   desc='process mineru layout')
        mineru_table_body_bboxs, mineru_complete_figure_table_bboxs, pages_images_contain_tables_and_figures_pathss = map(list, zip(*res))

        return page_image_pathss, mineru_texts, mineru_table_body_bboxs, mineru_complete_figure_table_bboxs, pages_images_contain_tables_and_figures_pathss
    
    def agent_chemical_structure_mllm_inference(self, names, bboxes_with_pred_smiless, mineru_complete_figure_table_bboxs):

        args = [
                (
                    name,
                    bboxes_with_pred_smiles,
                    mineru_complete_figure_table_bbox,
                    self.page_image_path,
                    self.augment_full_markush_path,
                    self.extraction_result_path,
                    self.vision_mllm_type,
                    self.base_url,
                    self.api_key,
                    self.structure_full_prompt,
                    self.structure_part_prompt,
                    self.structure_full_suffix,
                    self.structure_part_suffix,
                    self.structure_cot,
                    self.split_bbox_num,
                    self.segment_image,
                    self.enlarge_size,
                    self.structure_full_layout_seg,
                    self.structure_part_layout_seg,
                    self.bbox_background,
                    self.overwrite_structure_full,
                    self.overwrite_structure_part
                )
                for name, bboxes_with_pred_smiles, mineru_complete_figure_table_bbox
                in zip(names, bboxes_with_pred_smiless, mineru_complete_figure_table_bboxs)
            ]

        # Run in parallel using pmap_multi
        structure_data_lists = pmap_multi(
            process_single_pdf_chemical_structure_mllm,
            args,
            n_jobs=self.n_jobs,
            desc='Processing chemical structure MLLM inference'
        )
            
        return structure_data_lists

    def agent_chemical_structure(self, names, bboxes_with_pred_smiless, mineru_complete_figure_table_bboxs):

        extracetd_chemical_structures = self.agent_chemical_structure_mllm_inference(names, bboxes_with_pred_smiless, mineru_complete_figure_table_bboxs)

        return extracetd_chemical_structures
    
    def agent_bioactivity_measurement(self, names, pdf_texts, pdf_image_pathss):
        
        args = [
            (
                name,
                pdf_text,
                pdf_image_paths,
                self.text_mllm_type,
                self.vision_mllm_type,
                self.base_url,
                self.api_key,
                self.bioactivity_text_prompt,
                self.bioactivity_image_prompt,
                self.merge_strategy,
                self.extraction_result_path,
                self.bioactivity_text_suffix,
                self.bioactivity_image_suffix,
                self.bioactivity_cot,
                self.overwrite_bioactivity_text,
                self.overwrite_bioactivity_image
            )
            for name, pdf_text, pdf_image_paths
            in zip(names, pdf_texts, pdf_image_pathss)
        ]

        # Run in parallel using pmap_multi
        bioactivity_data_lists = pmap_multi(
            process_single_bioactivity_measurement,
            args,
            n_jobs=self.n_jobs,
            desc='Processing bioactivity measurement'
        )

        return bioactivity_data_lists
    
    def agent_postprocess(self, names, bioactivity_data_list, structure_data_list):
        df_extracted_overall_data_list = []
        for name, bioactivity_data, structure_data in tqdm(zip(names, bioactivity_data_list, structure_data_list), desc='postprocessing'):
            df_extracted_overall_data = save_overall_result(name, 
                                                            bioactivity_data, 
                                                            structure_data,
                                                            self.extraction_result_path, 
                                                            self.structure_full_suffix, 
                                                            self.structure_part_suffix)
            df_extracted_overall_data_list.append(df_extracted_overall_data)

        return df_extracted_overall_data_list
    
    def save_results_from_old_version_debug(self, names, bboxes_with_pred_smiless, mineru_complete_figure_table_bboxs):
       
        json_data = json.dumps(bboxes_with_pred_smiless, indent=4)
        with open(f'{self.output_dir}/{self.task_name}_ocsr_output.json', 'w') as f:
            f.write(json_data)

        augmented_full_image_pathss, augmented_part_image_pathss, index_smiles_dicts, image2bboxindexs = [], [], [], []

        res_list = pmap_multi(prepare_full_markush_process, 
                            zip(names, bboxes_with_pred_smiless), 
                            page_image_dir=self.page_image_path, 
                            save_path=self.augment_full_markush_path,
                            n_jobs=self.n_jobs,
                            desc='preparing markush process data')

        for res in res_list:
            augmented_full_image_paths, augmented_part_image_paths, index_smiles_dict, image2bboxindex = res
            augmented_full_image_pathss.append(augmented_full_image_paths)
            augmented_part_image_pathss.append(augmented_part_image_paths)
            index_smiles_dicts.append(index_smiles_dict)
            image2bboxindexs.append(image2bboxindex)

        # for name, bboxes_with_pred_smiles in tqdm(zip(names, bboxes_with_pred_smiless), desc='preparing markush process data '):
        #     augmented_full_image_paths, augmented_part_image_paths, index_smiles_dict, image2bboxindex = prepare_full_markush_process(name, bboxes_with_pred_smiles, self.page_image_path, self.augment_full_markush_path)
            
        #     augmented_full_image_pathss.append(augmented_full_image_paths)
        #     augmented_part_image_pathss.append(augmented_part_image_paths)
        #     index_smiles_dicts.append(index_smiles_dict)
        #     image2bboxindexs.append(image2bboxindex)

        # save mol_det_and_rec_res
        res = {}
        for name, augmented_full_image_paths, augmented_part_image_paths, index_smiles_dict in zip(names, augmented_full_image_pathss, augmented_part_image_pathss, index_smiles_dicts):
            res[name] = (augmented_full_image_paths, augmented_part_image_paths, index_smiles_dict)

        with open(f'{self.output_dir}/{self.task_name}_test_mol_dec_and_rec_file.pkl', 'wb') as f:
            pickle.dump(res, f) 

        # save image2bboxindex
        total_image2bboxindex = {}
        for image2bboxindex in image2bboxindexs:
            for key in image2bboxindex.keys():
                total_image2bboxindex[key] = image2bboxindex[key]

        json_data = json.dumps(total_image2bboxindex, indent=4)
        with open(f'{self.output_dir}/{self.task_name}_test_image2bbox.json', 'w') as f:
            f.write(json_data)

        # save layoutsegbbox
        total_middle_json = {}
        for d_name, minuer_figure_table_bbox_dict in zip(names, mineru_complete_figure_table_bboxs):
            total_middle_json[d_name] = minuer_figure_table_bbox_dict

        new_json_data = json.dumps(total_middle_json, indent=4)
        with open(f'{self.output_dir}/{self.task_name}_test_layout.json', 'w') as f:
            f.write(new_json_data)

        return

    def run_mol_det_total_batch(self, names, page_image_pathss, mineru_table_body_bboxs, batch_size):
        
        # =======================================================
        # Phase 1: 并行预处理 (Parallel Pre-processing)
        # 目的：裁剪表格，生成所有待检测的图片路径列表
        # =======================================================
        
        # 构造参数列表 (zip 将数据打包成元组)
        # 注意：不要传递 self，提取需要的字符串参数
        pre_args = list(zip(
            names, 
            page_image_pathss, 
            mineru_table_body_bboxs
        ))
        
        # kwargs 传递固定参数
        pre_kwargs = {
            'page_image_root': self.page_image_path,
            'full_page_save_dir': self.full_page_detection_path,
            'seg_table_save_dir': self.seg_table_detection_path
        }

        print(f"Phase 1: Pre-processing {len(names)} documents parallelly...")
        # 运行多进程
        pre_results = pmap_multi(worker_preprocess_doc, pre_args, n_jobs=self.n_jobs, desc="Pre-processing", **pre_kwargs)

        # =======================================================
        # Phase 2: 全局数据展平 (Flattening)
        # 目的：将多文档的数据合并成一个巨大的列表，供 GPU 跑大 Batch
        # =======================================================
        
        global_full_paths = []
        global_full_save_paths = []
        global_seg_paths = []
        global_seg_save_paths = []

        # 记录每个文档拥有多少张图片，用于后续切分 (Slice)
        doc_full_counts = []
        doc_seg_counts = []

        for res in pre_results:
            # Full page
            global_full_paths.extend(res['full_paths'])
            global_full_save_paths.extend(res['full_save_paths'])
            doc_full_counts.append(len(res['full_paths']))
            
            # Segmented table
            global_seg_paths.extend(res['seg_paths'])
            global_seg_save_paths.extend(res['seg_save_paths'])
            doc_seg_counts.append(len(res['seg_paths']))

        # =======================================================
        # Phase 3: GPU 集中推理 (Global GPU Inference)
        # 目的：利用 GPU Batch 优势
        # =======================================================
        
        # 3.1 跑全页检测 (如果需要)
        global_full_bboxes_flat = []
        if global_full_paths:
            print(f"Phase 2a: GPU Inference (Full Page) on {len(global_full_paths)} images...")
            # 使用之前定义的 global batch yolo 函数
            global_full_bboxes_flat = run_yolo_batch_global_client(
                global_full_paths, global_full_save_paths, self.grounding_gpu_num, batch_size=batch_size
            )
        
        # 3.2 跑表格检测
        global_seg_bboxes_flat = []
        if global_seg_paths:
            print(f"Phase 2b: GPU Inference (Table Seg) on {len(global_seg_paths)} images...")
            global_seg_bboxes_flat = run_yolo_batch_global_client(
                global_seg_paths, global_seg_save_paths, self.grounding_gpu_num, batch_size=batch_size
            )

        # =======================================================
        # Phase 4: 数据分发与准备 (Distribution)
        # 目的：将扁平的 GPU 结果按文档切分，准备后处理参数
        # =======================================================
        
        post_args = []
        
        # 指针用于切分 flat 列表
        ptr_full = 0
        ptr_seg = 0

        for i, name in enumerate(names):
            # --- 还原全页结果 ---
            count_full = doc_full_counts[i]
            current_bboxes_list = global_full_bboxes_flat[ptr_full : ptr_full + count_full]
            ptr_full += count_full
            # 格式化：加上 page 索引 (注意预处理时是按 page_image_paths 顺序加入的，即 page 0, 1, 2...)
            doc_full_res = []
            for page_idx, bboxes in enumerate(current_bboxes_list):
                doc_full_res.extend([{'page': page_idx, 'bbox': bbox} for bbox in bboxes])

            # --- 还原表格结果 ---
            count_seg = doc_seg_counts[i]
            current_seg_bboxes_list = global_seg_bboxes_flat[ptr_seg : ptr_seg + count_seg]
            ptr_seg += count_seg
            
            # 获取预处理时存的 layout 和 page 信息
            layouts = pre_results[i]['seg_layouts']
            pages = pre_results[i]['seg_pages']
            
            doc_seg_res = []
            for page, layout, bboxes in zip(pages, layouts, current_seg_bboxes_list):
                doc_seg_res.append({'page': page, 'tb_layout_bbox': layout, 'bboxes': bboxes})

            # 准备后处理的单个参数
            post_args.append((
                name,
                doc_full_res,
                doc_seg_res
            ))

        # =======================================================
        # Phase 5: 并行后处理 (Parallel Post-processing)
        # 目的：并行合并结果、画图、保存
        # =======================================================
        
        post_kwargs = {
            'page_image_root': self.page_image_path,
            'merge_detection_path': self.merge_detection_path
        }

        print(f"Phase 3: Post-processing {len(names)} documents parallelly...")
        post_results = pmap_multi(worker_postprocess_doc, post_args, n_jobs=self.n_jobs, desc="Post-processing", **post_kwargs)

        # 解包结果
        merge_pdf_bboxess = [res[0] for res in post_results]
        all_segmented_box_pathss = [res[1] for res in post_results]

        return all_segmented_box_pathss, merge_pdf_bboxess

    def run_ocsr_global_batch(self, names, merge_pdf_bboxess, all_segmented_box_pathss, batch_size=64):
        """
        重构后的 OCSR 批量处理函数
        """
        # 数据收集与映射 (Data Collection & Mapping)
        global_img_paths = []
        # 映射表：记录全局列表第 i 个图片对应 (文档索引, bbox索引)
        map_indices = [] 

        # 遍历所有文档
        for doc_idx, (all_segmented_box_paths, merge_pdf_bboxes) in enumerate(zip(all_segmented_box_pathss, merge_pdf_bboxess)):
            # 确保图片路径和 bbox 数量一致
            if len(all_segmented_box_paths) != len(merge_pdf_bboxes):
                print(f"Warning: Doc {doc_idx} image count {len(all_segmented_box_paths)} != bbox count {len(merge_pdf_bboxes)}")
                continue
                
            for bbox_idx, img_path in enumerate(all_segmented_box_paths):
                global_img_paths.append(img_path)
                map_indices.append((doc_idx, bbox_idx))

        # 全局批量推理 (Global Batch Inference)
        print(f"Running OCSR on {len(global_img_paths)} molecules...")
        total_images = len(global_img_paths)

        # 分批次处理，防止一次性把几万张图读入内存导致 OOM
        global_predictions_smiles = []
        global_predictions_captions = []

        def do_parse(file_path, url='http://127.0.0.1:8003/predict', **kwargs):
            payload = {'image_paths': file_path}
            try:
                response = requests.post(url, json=payload, timeout=300)
                if response.status_code == 200:
                    return response.json()['results']
                else:
                    return [''] * len(file_path)
            except Exception as e:
                logger.error(f'File: {file_path} - Info: {e}')

        batches = [] 
        for i in range(0, total_images, batch_size):
            batch_paths = global_img_paths[i : i + batch_size]
            batches.append(batch_paths)

        n_jobs = np.clip(len(batches), 1, self.grounding_gpu_num)
        results = Parallel(n_jobs, prefer='threads', verbose=10)(
            delayed(do_parse)(b) for b in batches
        )

        # for i in tqdm(range(0, len(global_img_paths), batch_size), desc="OCSR Batch Inference"):
        #     batch_paths = global_img_paths[i : i + batch_size]
        #     batch_outputs = ocsr_model.predict_image_files(batch_paths, return_atoms_bonds=False, return_confidence=False)
        
        for batch_index, batch_outputs in enumerate(results):
            # 立即进行后处理 (SMILES Refactor) 以释放 raw output 内存
            if batch_index == 0:
                print(batch_outputs)
            for raw_output in batch_outputs:
                try:
                    # 保持原有的 refactor 逻辑
                    pred_e_smi = raw_output
                    pred_smi = get_refactor(Translator.refactor(raw_output))

                    # print(pred_e_smi)
                    smi_of_e_smi, extend_of_e_smi = pred_e_smi.split('<sep>')[0], pred_e_smi.split('<sep>')[1]
                    
                    if '<r>' in extend_of_e_smi or '<c>' in extend_of_e_smi:
                        pred_smi = None
                    else:
                        pred_smi = get_new_smiles(pred_smi, smi_of_e_smi, extend_of_e_smi)

                except Exception as e:
                    # 增加容错，防止单个分子解析失败卡死整个流程
                    # print(f"Refactor error: {e}")
                    pred_smi = "" 
                global_predictions_smiles.append(pred_smi)
                global_predictions_captions.append(raw_output)

        # 结果回填 (Distribute Results)
        # 将扁平化的结果填回原始的层级结构中
        for (doc_idx, bbox_idx), smiles, caption, img_path in zip(map_indices, global_predictions_smiles, global_predictions_captions, global_img_paths):
            # 直接修改原列表对象
            merge_pdf_bboxess[doc_idx][bbox_idx]['smiles'] = smiles
            merge_pdf_bboxess[doc_idx][bbox_idx]['caption'] = caption
            merge_pdf_bboxess[doc_idx][bbox_idx]['img_path'] = img_path

        # 如果需要返回，根据你的接口约定返回；
        # 因为上面是原地修改(in-place modification)，merge_pdf_bboxess 已经被更新了
        return merge_pdf_bboxess 

    def opensource(self, pdf_paths):

        if isinstance(pdf_paths, str):
            pdf_paths = [pdf_paths]

        names = self.init_pred_dir(pdf_paths)

        if os.path.exists(self.stage_one_result_path):
            with open(self.stage_one_result_path, 'rb') as f:
                page_image_pathss, mineru_texts, mineru_table_body_bboxs, mineru_complete_figure_table_bboxs, pages_images_contain_tables_and_figures_pathss, merge_pdf_bboxess, all_segmented_box_pathss, bboxes_with_pred_smiless = pickle.load(f)
        else:
            if not os.path.exists(self.stage_preprocess_result_path):
                page_image_pathss, mineru_texts, mineru_table_body_bboxs, mineru_complete_figure_table_bboxs, pages_images_contain_tables_and_figures_pathss = self.agent_preprocess(names, pdf_paths)
                with open(self.stage_preprocess_result_path, 'wb') as f:
                    pickle.dump((page_image_pathss, mineru_texts, mineru_table_body_bboxs, mineru_complete_figure_table_bboxs, pages_images_contain_tables_and_figures_pathss), f)
                print(f'saving preprocessing part 1 results')
            else:
                with open(self.stage_preprocess_result_path, 'rb') as f:
                    temp_data = pickle.load(f)
                page_image_pathss, mineru_texts, mineru_table_body_bboxs, mineru_complete_figure_table_bboxs, pages_images_contain_tables_and_figures_pathss = temp_data
            
            all_segmented_box_pathss, merge_pdf_bboxess = [], []
            all_segmented_box_pathss, merge_pdf_bboxess = self.run_mol_det_total_batch(names, page_image_pathss, mineru_table_body_bboxs, batch_size=256)

            bboxes_with_pred_smiless = self.run_ocsr_global_batch(names, merge_pdf_bboxess, all_segmented_box_pathss, batch_size=256)

            with open(self.stage_one_result_path, 'wb') as f:
                pickle.dump((page_image_pathss, mineru_texts, mineru_table_body_bboxs, mineru_complete_figure_table_bboxs, pages_images_contain_tables_and_figures_pathss, merge_pdf_bboxess, all_segmented_box_pathss, bboxes_with_pred_smiless), f)
            
            self.save_results_from_old_version_debug(names, bboxes_with_pred_smiless, mineru_complete_figure_table_bboxs)
            print(f'saving preprocessing results')

        extracetd_chemical_structure_lists = self.agent_chemical_structure_mllm_inference(names, bboxes_with_pred_smiless, mineru_complete_figure_table_bboxs)
        bioactivity_data_lists = self.agent_bioactivity_measurement(names, mineru_texts, pages_images_contain_tables_and_figures_pathss)
        df_extracted_overall_data_list = self.agent_postprocess(names, bioactivity_data_lists, extracetd_chemical_structure_lists)
        if self.biovista_evaluate:
            self.evaluate_biovista(names)
        return bioactivity_data_lists, extracetd_chemical_structure_lists, df_extracted_overall_data_list
    

    def evaluate_biovista(self, names):
        result = resulter(names, self.top_n, self.extraction_result_path, self.extraction_result_path, self.structure_full_suffix, self.structure_part_suffix)
        result.initialize_evaluating_result()

        evaluation_results = pmap_multi(evaluate_step, 
                                        zip(names),
                                        pdb_name_path=self.pdb_name_path, 
                                        pdb_label_path=self.pdb_label_path, 
                                        pdb_structure_path=self.pdb_structure_path,
                                        labels_base_dir=self.labels_base_dir, 
                                        dataset_name=self.dataset_name, 
                                        text_model_output_path=self.extraction_result_path,
                                        vision_model_output_path=self.extraction_result_path,
                                        structure_full_suffix=self.structure_full_suffix,
                                        structure_part_suffix=self.structure_part_suffix,
                                        bioactivity_text_suffix=self.bioactivity_text_suffix,
                                        bioactivity_image_suffix=self.bioactivity_image_suffix,
                                        top_n=self.top_n,
                                        n_jobs=self.n_jobs,
                                        desc='biovista evaluating ...'
                                        )
        for name, evaluation_result in zip(names, evaluation_results):
            result.update_evaluating_result(name, evaluation_result)

        result.output_evaluating_result()

        return



class BioMiner_Markush_Infernce(object):
    def __init__(self, vision_mllm_type, markush_prompt_path, 
                 image2bboxindex_path=None, layout_seg_json_path=None,
                 context_examples=None, base_url=None, api_key=None):
        with open(markush_prompt_path, 'r') as f:
            self.markush_prompt = f.read().strip()
        
        self.vision_mllm_type = vision_mllm_type
        self.base_url = base_url
        self.api_key = api_key

        self.image2bboxindex_path = image2bboxindex_path
        self.layout_seg_json_path = layout_seg_json_path
        self.context_examples = context_examples

        if image2bboxindex_path is not None:
            with open(image2bboxindex_path, 'r') as f:
                image2bboxindex = json.load(f)
            self.image2bboxindex = image2bboxindex

        if layout_seg_json_path is not None:
            with open(layout_seg_json_path, 'r') as f:
                layoutsegbbox = json.load(f)
            self.layoutsegbbox = layoutsegbbox

    def markush_zip_with_index_batch_split_image_layout(self, image_paths, split_bbox_num, segment_image, cot=False):
        
        assert self.image2bboxindex_path is not None
        assert self.layout_seg_json_path is not None
        image_bbox_dicts = []
        figure_table_layout_bboxs = []
        for image_path in image_paths:
            file_name = os.path.basename(image_path)
            image_bbox_dicts.append(self.image2bboxindex[file_name])

            file_name_items = file_name.split('.')[0].split('_')
            pdf_idex = file_name_items[0]
            pdf_pdb_name = file_name_items[1]
            pdf_name = f'{pdf_idex}_{pdf_pdb_name}'
            page_idx = file_name_items[-1]
            
            try:
                figure_table_layout_bboxs.append(self.layoutsegbbox[pdf_name][page_idx])
            except:
                figure_table_layout_bboxs.append(None)

        data_jsons = pmap_multi(extract_markush_part_with_bbox_index_split_complex_image_seg_layout, 
                                zip(image_paths, image_bbox_dicts, figure_table_layout_bboxs),
                                markush_prompt=self.markush_prompt,
                                vision_mllm_type=self.vision_mllm_type,
                                cot=cot, split_bbox_num=split_bbox_num,
                                segment_image=segment_image,
                                base_url=self.base_url, api_key=self.api_key,
                                n_jobs=16, desc='extracting markush structures ')

        return data_jsons
