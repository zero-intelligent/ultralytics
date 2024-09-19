from ultralytics.engine.results import Results
from copy import deepcopy
import torch
import time
from ultralytics.utils.plotting import Annotator
from mcd.event import config_changed_event


class PersonResults(Results):
    id_info_tracker = {}
    total_time_info = {}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # 覆盖基类的方法，否则复制对象时，类型信息又回去了
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
            img = (self.orig_img[0].detach().permute(
                1, 2, 0).contiguous() * 255).to(torch.uint8).cpu().numpy()

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
            # Classify tasks default to pil=True
            pil or (pred_probs is not None and show_probs),
            example=names,
        )
        
        # Plot Detect results
        if pred_boxes is not None and show_boxes:
            current_time = time.time()
            for d in reversed(pred_boxes):
                c, conf, id = int(d.cls), float(d.conf) if conf else None, None if d.id is None else int(d.id.item())
                if not id:
                    continue
                
                if id not in PersonResults.id_info_tracker:
                    id_info = {
                        'start_time': current_time,
                        'total_time': 0,
                        'path': [[int((float(d.xyxy[0][0]) + float(d.xyxy[0][2]))/2),
                                  int((float(d.xyxy[0][1]) + float(d.xyxy[0][3]))/2)]]
                    }
                    PersonResults.id_info_tracker[id] = id_info
                else:
                    id_info = PersonResults.id_info_tracker[id]
                    if id_info['start_time']:
                        id_info['total_time'] += current_time - id_info['start_time']
                    id_info['start_time'] = current_time
        
                    id_info['path'] += [[int((float(d.xyxy[0][0]) + float(d.xyxy[0][2]))/2),# 添加路径坐标
                                        int((float(d.xyxy[0][1]) + float(d.xyxy[0][3]))/2)]]
                
                label = f"id:{id},{int(id_info['total_time'])}s"
                xy = [int((float(d.xyxy[0][0]) + float(d.xyxy[0][2]))/2)-8, int(d.xyxy[0][1])]
                annotator.text(xy, label, txt_color=(48, 128, 20), box_style=True)
                annotator.routing_path(id_info['path'], color=(48, 128, 20))
                
            # 检查离开屏幕的人员
            box_person_ids = [int(d.id.item()) for d in reversed(pred_boxes) if d.id]
            for person_id, data in PersonResults.id_info_tracker.items():
                if person_id not in box_person_ids:
                    # 如果该 person_id 不再出现在当前检测结果中，则停止计时并记录时间
                    if data['start_time'] is not None:
                        PersonResults.id_info_tracker[person_id]['total_time'] += current_time - data['start_time']
                        # 将 start_time 置为空表示该人离开
                        PersonResults.id_info_tracker[person_id]['start_time'] = None
            
            #评估是否发送
            total_time_info = {id: int(v['total_time']) for id,v in PersonResults.id_info_tracker.items() if int(v['total_time']) > 0}
            if total_time_info != PersonResults.total_time_info:
                PersonResults.total_time_info = total_time_info
                config_changed_event.set()  # 表示人员统计信息已经有更新
                
        # Plot Classify results
        if pred_probs is not None and show_probs:
            text = ",\n".join(f"{names[j] if names else j} {pred_probs.data[j]:.2f}" for j in pred_probs.top5)
            x = round(self.orig_shape[0] * 0.03)
            # TODO: allow setting colors
            annotator.text([x, x], text, txt_color=(255, 255, 255))

        # Plot Pose results
        if self.keypoints is not None:
            for k in reversed(self.keypoints.data):
                annotator.kpts(k, self.orig_shape,
                               radius=kpt_radius, kpt_line=kpt_line)

        # Show results
        if show:
            annotator.show(self.path)

        # Save results
        if save:
            annotator.save(filename)

        return annotator.result()
