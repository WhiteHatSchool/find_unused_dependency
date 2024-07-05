#!/bin/bash

# syft 설치
sudo curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin

# java 설치
sudo apt install openjdk-17-jdk

# 파이썬 설치
sudo apt-get install python3
sudo apt-get install pip3

# 파이썬 스크립트 실행
python3 setup.py

# 가상 환경 활성화
source myenv/bin/activate
