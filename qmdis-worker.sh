#!/bin/bash -e

BASEDIR=$(dirname $0)

counter=1
while [ $counter -le 5 ]
do
echo  running worker w$counter
screen -dmS w$counter sh
screen -S w$counter -p 0 -X stuff ". ~/kgs_env/bin/activate
"
screen -S w$counter -p 0 -X stuff "export GST_PLUGIN_PATH=/home/qcri/gst-kaldi-nnet2-online/src
"
screen -S w$counter -p 0 -X stuff "cd /home/qcri/kaldi-gstreamer-server/
"
screen -S w$counter -p 0 -X stuff "python kaldigstserver/worker.py -u wss://localhost:8888/worker/ws/speech -c /opt/model/model.yaml
"
sleep 2
((counter++))
done

