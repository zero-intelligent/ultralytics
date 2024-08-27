#!/bin/bash

cd gui
npm run build

cd ../
python -m build
