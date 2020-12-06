#!/bin/bash -e

BASEDIR=$(dirname $0)

screen -dmS apiserver sh
screen -S apiserver -p 0 -X stuff ". ~/kgs_env/bin/activate
"
screen -S apiserver -p 0 -X stuff " cd dialectid_api
"
screen -S apiserver -p 0 -X stuff "python api_adi.py
"

sleep 2



