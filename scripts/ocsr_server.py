# server.py
import os
import torch
import litserve as ls
from fastapi import HTTPException
import logging
import gc

from BioMiner.MolScribe.molscribe import MolGlyph

from BioMiner.commons.molglyph_utils import Translator, get_refactor, get_new_smiles

# -----------------------------------------------------------

class MolGlyphAPI(ls.LitAPI):
    def setup(self, device):
        # 1. 设置设备和加载模型
        print(f"Initializing model on {device}...")
        self.device = device
        
        # 模型路径 (建议配置化)
        model_path = 'scripts/molglyph_large.pt'
        
        # 初始化模型
        self.ocsr_model = MolGlyph(model_path, self.device)
        print(f"Model loaded successfully on {device}")

    def decode_request(self, request):
        # 2. 解析请求
        # 接收格式: {"image_paths": ["/path/1.png", "/path/2.png"], "kwargs": {...}}
        img_paths = request.get("image_paths", [])
        if not img_paths:
            raise HTTPException(status_code=400, detail="No image paths provided")
        
        return img_paths

    def predict(self, img_paths):
        # 3. 执行推理
        # print(f"Processing batch of {len(img_paths)} images...")
        # print(f'input {img_paths}')
        try:
            # 调用 MolGlyph 原始推理接口
            # 注意：这里假设 predict_image_files 支持传入 list
            with torch.no_grad():
                batch_outputs = self.ocsr_model.predict_image_files(
                    img_paths, 
                    return_atoms_bonds=False, 
                    return_confidence=False
                )
            return batch_outputs

        except Exception as e:
            # 整个 Batch 失败
            logging.error(f"Inference failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            self.clean_memory()


    def encode_response(self, output):
        # 5. 返回结果
        return {"results": output}
    
    def clean_memory(self):
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
        gc.collect()

if __name__ == '__main__':
    # 配置多卡服务
    server = ls.LitServer(
        MolGlyphAPI(),
        accelerator="cuda",
        devices=[0, 1, 2, 3],  # 指定使用的 GPU ID
        workers_per_device=1,  # 每个 GPU 跑一个模型实例
        timeout=False         # 禁用超时，防止大 Batch 处理时间过长断开
    )
    
    print("Starting MolGlyph 4-GPU Server on port 8003...")
    server.run(port=8003)