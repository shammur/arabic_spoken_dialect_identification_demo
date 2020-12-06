#!/bin/bash -e

BASEDIR=$(dirname $0)

screen -dmS kgserver sh
screen -S kgserver -p 0 -X stuff ". ~/kgs_env/bin/activate
"
screen -S kgserver -p 0 -X stuff "cd ~/kaldi-gstreamer-server/
"
screen -S kgserver -p 0 -X stuff "python kaldigstserver/master_server.py --port=8888 --certfile=/etc/ssl/wildcard.qcri.org.2020.crt --keyfile=/etc/ssl/wildcard.qcri.org.key
"

sleep 2


