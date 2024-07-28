import torch
import json

from config import ModelConfig

MODELCONFIG = ModelConfig()


class ONNX_Model:
    def __init__(self) -> None:
        # self.Models = torch.hub.load(
        #     "./yolov5",
        #     "custom",
        #     path=MODEL_PATH,
        #     force_reload=True,
        #     source='local'
        # )
        self.model = torch.hub.load(
            repo_or_dir="ultralytics/yolov5",
            model="custom",
            path=MODELCONFIG.model_path,
            force_reload=True,
            skip_validation=True,
        )
        self.model.conf = MODELCONFIG.conf
        self.model.iou = MODELCONFIG.iou

    def get_label(self, im):
        results = self.model(im, size=640)
        results = json.loads(results.pandas().xyxy[0].to_json(orient="records"))
        return results
