from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2.data import MetadataCatalog
from detectron2.utils.visualizer import ColorMode, Visualizer
from detectron2 import model_zoo

import cv2
import numpy as np


class Detector:
    def __init__(self, model_type="OD"):
        self.cfg = get_cfg()
        self.model_type = model_type
        cfg_files = {
            "OD": "COCO-Detection/faster_rcnn_R_101_FPN_3x.yaml",
            "IS": "COCO-InstanceSegmentation/mask_rcnn_R_50_FPN_3x.yaml",
            "KP": "COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml",
            "PS": "COCO-PanopticSegmentation/panoptic_fpn_R_101_3x.yaml",
        }

        # Load model config and pretrained model
        self.cfg.merge_from_file(model_zoo.get_config_file(cfg_files[self.model_type]))
        self.cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url(
            cfg_files[self.model_type]
        )

        self.cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.7
        self.cfg.MODEL.DEVICE = "cpu"  # cpu or cuda
        self.parallel = True
        self.predictor = DefaultPredictor(self.cfg)

    def onImage(self, imagePath):
        image = cv2.imread(imagePath)
        if self.model_type != "PS":
            predictions = self.predictor(image)

            viz = Visualizer(
                image[:, :, ::-1],
                metadata=MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]),
                instance_mode=ColorMode.IMAGE,
            )  # SEGMENTATION, IMAGE, IMAGE_BW

            output = viz.draw_instance_predictions(predictions["instances"].to("cpu"))
        else:
            predictions, segmentInfo = self.predictor(image)["panoptic_seg"]
            # print(predictions)
            # print(segmentInfo)
            # viz = Visualizer(image[:,:,::-1], MetadataCatalog.get(self.cfg.DATASETS.TRAIN[0]))
            # output = viz.draw_panoptic_seg_predictions(predictions.to("cpu"), segmentInfo)
            return predictions, segmentInfo

            # Wall mask
            # objectId = next((sub for sub in segmentInfo if sub['category_id'] == 52), { 'id': 0 })['id']

            # mask = image.copy()
            # xpx, ypx, bitpx = image.shape
            # for i in range(xpx):
            # 	for j in range(ypx):
            # 		if predictions[i][j] == objectId:
            # 			mask[i][j] = (255, 0, 0)
            # mask = cv2.resize(mask, (0, 0), fx = 0.5, fy = 0.5)
            # cv2.imshow("wall", mask)

        # half = cv2.resize(output.get_image()[:,:,::-1], (0, 0), fx = 0.5, fy = 0.5)
        # cv2.imshow("Result", half)
        # cv2.waitKey(0)
