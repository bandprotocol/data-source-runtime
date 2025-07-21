#!/bin/bash
apt-get update
apt-get install zip 

cd /pack
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd venv/lib/python3.13/site-packages
zip -r9 ${OLDPWD}/lambda-executor.zip .

cd ${OLDPWD}
deactivate
rm -r venv
zip -g lambda-executor.zip lambda_function.py
