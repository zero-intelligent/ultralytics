from ultralytics.engine.results import Results
from copy import deepcopy
from functools import lru_cache
from pathlib import Path

import numpy as np
import torch

from ultralytics.data.augment import LetterBox
from ultralytics.utils import LOGGER, SimpleClass, ops
from ultralytics.utils.plotting import Annotator, colors, save_one_box
from ultralytics.utils.torch_utils import smart_inference_mode

class PersonResults(Results):
    id_info = {}

    # 覆盖基类的方法，否则复制对象时，类型信息又回去了

    def __init__(
        self, **kwargs
    ) -> None:
        super().__init__(**kwargs)

    def new(self):
        return PersonResults(orig_img=self.orig_img, path=self.path, names=self.names, speed=self.speed)
    
    def plot(self,
            conf=True,
            line_width=None,
            font_size=None,
            font="Arial.ttf",
            pil=False,
            img=None,
            im_gpu=None,
            kpt_radius=5,
            kpt_line=True,
            labels=True,
            boxes=True,
            masks=True,
            probs=True,
            show=False,
            save=False,
            filename=None
        ):
        if img is None and isinstance(self.orig_img, torch.Tensor):
            img = (self.orig_img[0].detach().permute(1, 2, 0).contiguous() * 255).to(torch.uint8).cpu().numpy()

        names = self.names
        is_obb = self.obb is not None
        pred_boxes, show_boxes = self.obb if is_obb else self.boxes, boxes
        pred_masks, show_masks = self.masks, masks
        pred_probs, show_probs = self.probs, probs
        annotator = Annotator(
            deepcopy(self.orig_img if img is None else img),
            line_width,
            font_size,
            font,
            pil or (pred_probs is not None and show_probs),  # Classify tasks default to pil=True
            example=names,
        )

        # Plot Detect results
        if pred_boxes is not None and show_boxes:
            for d in reversed(pred_boxes):
                c, conf, id = int(d.cls), float(d.conf) if conf else None, None if d.id is None else int(d.id.item())
                if not id:
                    continue
                if id not in PersonResults.id_info:
                    PersonResults.id_info[id] = {
                        "time_s": 0.0,
                        "path": [[int((float(d.xyxy[0][0]) + float(d.xyxy[0][2]))/2),
                                  int((float(d.xyxy[0][1]) + float(d.xyxy[0][3]))/2)]]
                    }
                else:
                    PersonResults.id_info[id]['time_s'] += 1.0/20  # 每发现一帧，积累每帧的时间
                    PersonResults.id_info[id]['path'] += [[int((float(d.xyxy[0][0]) + float(d.xyxy[0][2]))/2),
                                                     int((float(d.xyxy[0][1]) + float(d.xyxy[0][3]))/2)]] # 添加路径坐标
                    
                label = f"id:{id},{int(PersonResults.id_info[id]['time_s'])}s"
                xy = [int((float(d.xyxy[0][0]) + float(d.xyxy[0][2]))/2)-8,int(d.xyxy[0][1])]
                annotator.text(xy, label, txt_color=(48,128,20),box_style=True)
                annotator.routing_path(PersonResults.id_info[id]['path'],color=(48,128,20))

        # Plot Classify results
        if pred_probs is not None and show_probs:
            text = ",\n".join(f"{names[j] if names else j} {pred_probs.data[j]:.2f}" for j in pred_probs.top5)
            x = round(self.orig_shape[0] * 0.03)
            annotator.text([x, x], text, txt_color=(255, 255, 255))  # TODO: allow setting colors

        # Plot Pose results
        if self.keypoints is not None:
            for k in reversed(self.keypoints.data):
                annotator.kpts(k, self.orig_shape, radius=kpt_radius, kpt_line=kpt_line)

        # Show results
        if show:
            annotator.show(self.path)

        # Save results
        if save:
            annotator.save(filename)

        return annotator.result()

