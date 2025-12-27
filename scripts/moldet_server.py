# server.py
import os
import torch
import litserve as ls
from fastapi import HTTPException
import logging
from ultralytics import YOLO
from PIL import Image
from BioMiner.commons.process_pdf import draw_bbox_xywh

# -----------------------------------------------------------

class MolGlyphAPI(ls.LitAPI):
    def setup(self, device):
        # 1. 设置设备和加载模型
        print(f"Initializing model on {device}...")
        self.device = device
        
        # 模型路径 (建议配置化)        
        self.det_model =  YOLO("BioMiner/commons/moldet_v2_yolo11n_960_doc.pt").to(device)
        print(f"Model loaded successfully on {device}")

    def decode_request(self, request):
        # 2. 解析请求
        # 接收格式: {"image_paths": ["/path/1.png", "/path/2.png"], "kwargs": {...}}
        img_paths = request.get("image_paths", [])
        save_paths = request.get("save_paths", [])
        
        return img_paths, save_paths

    def predict(self, inputs):
        # 3. 执行推理
        # print(f"Processing batch of {len(img_paths)} images...")
        # print(f'input {img_paths}')
        img_paths = inputs[0]
        save_paths = inputs[1]

        iou_threshold=0.85
        imgs = [Image.open(img_path) for img_path in img_paths]
        try:
            # 调用 MolGlyph 原始推理接口
            # 注意：这里假设 predict_image_files 支持传入 list

            results1 = self.det_model.predict(imgs, imgsz=960, conf=0.5)

            all_bboxes = []
            
            for idx in range(len(imgs)):
                result1 = results1[idx]
                img = imgs[idx]
                save_path = save_paths[idx]
                img_width, img_height = img.size
                img_area = img_width * img_height
                
                # mols = []
                bboxes = []
                boxes1 = result1.boxes
                total_box_area = 0

                for xyxy in boxes1.xyxy:
                    x1, y1, x2, y2 = xyxy.detach().cpu().numpy()
                    box_area = (x2 - x1) * (y2 - y1)
                    total_box_area += box_area

                if total_box_area / img_area > iou_threshold:
                    # mols.append(img)
                    bboxes.append([0, 0, 1, 1])
                else:
                    for xyxy in boxes1.xyxy:
                        x1, y1, x2, y2 = xyxy.detach().cpu().numpy()
                        # mols.append(img.crop((x1, y1, x2, y2)))
                        bboxes.append([x1 / img_width, y1 / img_height, (x2-x1)/ img_width, (y2-y1)/img_height])

                    index = 0
                    for xyxy in boxes1.xyxy:
                        x1, y1, x2, y2 = xyxy.detach().cpu().numpy()
                        draw_bbox_xywh(img, x1 / img_width, y1 / img_height, (x2-x1)/ img_width, (y2-y1)/img_height, index)
                        index += 1

                if len(bboxes) > 0:
                    img.save(save_path)

                # all_mols.append(mols)
                all_bboxes.append(bboxes)

            return all_bboxes

        except Exception as e:
            # 整个 Batch 失败
            logging.error(f"Inference failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    def encode_response(self, output):
        # 5. 返回结果
        return {"all_bboxes": output}

if __name__ == '__main__':
    # 配置多卡服务
    server = ls.LitServer(
        MolGlyphAPI(),
        accelerator="cuda",
        devices=[2, 3, 4, 6],  # 指定使用的 GPU ID
        workers_per_device=1,  # 每个 GPU 跑一个模型实例
        timeout=False         # 禁用超时，防止大 Batch 处理时间过长断开
    )
    
    print("Starting MolDetv2 4-GPU Server on port 8001...")
    server.run(port=8001)