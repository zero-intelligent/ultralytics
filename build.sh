#!/bin/bash


if ! pip install -i https://mirrors.aliyun.com/pypi/simple build setuptools wheel; then
    echo "install module build setuptools wheel fail!"
    exit 1
fi
if ! python -m build; then
    echo "python -m build fail!"
    exit 1
fi

echo install success.