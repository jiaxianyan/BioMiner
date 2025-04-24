
import os
import argparse
from BioMiner import BioMiner
from BioMiner.commons.utils import get_config_easydict

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', type=str, default='BioMiner/config/default.yaml')
    parser.add_argument('--pdf', type=str, default='example/pdfs')
    parser.add_argument('--external_full_md_res_dir', type=str, default='example/full_md_molminer')
    parser.add_argument('--external_ocsr_res_dir', type=str, default='example/ocsr_molparser')
    parser.add_argument('--biovista_evaluate', action='store_true')
    args = parser.parse_args()
    
    config = get_config_easydict(args.config_path)

    model = BioMiner(config,
                     biovista_evaluate=args.biovista_evaluate)
    
    if os.path.isdir(args.pdf):
        files = os.listdir(args.pdf)
        pdf_paths = [os.path.join(args.pdf, f) for f in files]
    else:
        pdf_paths = [args.pdf]
        
    model.opensource_stage_one(pdf_paths)
