#!/bin/bash

apt-get update -y
apt-get install -y portaudio19-dev
pip install -r requirements.txt
