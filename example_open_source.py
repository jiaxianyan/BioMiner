
import os
import argparse
from BioMiner import BioMiner
from BioMiner.commons.utils import get_config_easydict

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_path', type=str, default='BioMiner/config/default.yaml')
    parser.add_argument('--pdf', type=str)
    parser.add_argument('--output_dir', type=str)
    parser.add_argument('--biovista_evaluate', action='store_true')

    args = parser.parse_args()
    
    config = get_config_easydict(args.config_path)

    config.output_dir = args.output_dir

    model = BioMiner(config,
                     biovista_evaluate=args.biovista_evaluate)
    
    if os.path.isdir(args.pdf):
        files = os.listdir(args.pdf)
        pdf_paths = [os.path.join(args.pdf, f) for f in files if '.pdf' in f]
    else:
        pdf_paths = [args.pdf]
        
    bioactivity_data_lists, extracetd_chemical_structure_lists, df_extracted_overall_data_list = model.opensource(pdf_paths)
    print(df_extracted_overall_data_list[0].dropna())
