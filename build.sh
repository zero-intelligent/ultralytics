#!/bin/bash

# cd gui
# npm run build

# cd ../
if ! pip install -i https://mirrors.aliyun.com/pypi/simple build setuptools wheel;then
    echo "install module build setuptools wheel fail!"
    exit 1
python -m build
