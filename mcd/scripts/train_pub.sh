#!/bin/bash

echo "备份服务器训练数据"
ssh -p 2222 admin@8.140.49.13 'cd python_projects/ultralytics/datasets;mv MCD MCD_$(date +"%Y%m%d%H")'

echo "复制训练数据到服务器"
scp -P 2222 -r ~/Downloads/MCD admin@8.140.49.13:/home/admin/python_projects/ultralytics/datasets/

echo "开始训练模型"
ssh -p 2222 admin@8.140.49.13 'cd python_projects/ultralytics;conda activate ultralytics; export PYTHONPATH=$(pwd);python mcd/train.py datasets/MCD'


echo "训练结果模型复制到本地"
dir=$(ssh -p 2222 admin@8.140.49.13 'ls /home/admin/python_projects/ultralytics/runs/detect/* -td | head -1')
scp -P 2222  admin@8.140.49.13:${dir}/weights/best.onnx ~/python_projects/ultralytics/mcd/weights/huiji.onnx

echo "本地训练模型复制到鲁班猫"
scp -P 2224 ~/python_projects/ultralytics/mcd/weights/huiji.onnx cat@8.140.49.13:/home/cat/app/ultralytics/mcd/weights/huiji.onnx

echo "重启鲁班猫服务"
ssh -p 2224 cat@8.140.49.13 'echo "temppwd" | sudo -S systemctl restart mcd-video-analysis.service'


