#!/home/qcri/kgs_env/bin/python
__author__ = "shchowdhury"
__date__ = "25-Feb-2020"
'''
#!/home/qcri/kgs_env/bin/python
#### comment #!/usr/bin/python

script that shows how to postprocess full results from the kaldi-gstreamer-worker, encoded as JSON.
'''


import os
import sys
import json
import logging
import time
import datetime
import contextlib
from io import BytesIO
import wave
# from arabic_dialect_identification.lexical import lexical_identification
from arabic_dialect_identification.acoustic import acoustic_identification4
logger = logging.getLogger(__name__)

class LastNTokens(object):
    def __init__(self, n):
        # last number of token to be reserved
        self.n = n
        self.session = None
        self.tokens = list()

    def get_n_tokens(self):
        # return self.tokens[-self.n:]
        return self.tokens[:]

    def add_tokens_list(self, tokens, sessionid):
        if self.session == sessionid:
            self.tokens.extend(tokens)
        else:
            self.session = sessionid
            self.tokens = tokens[:]
        # if len(self.tokens) > self.n:
        #     self.tokens = self.tokens[-self.n:]


token_list_10 = LastNTokens(10)

def post_process_json(json_str):
    logger.info("In post processor")
    try:
        # conf = {}
        # if args.conf:
        #     with open(args.conf) as f:
        #         conf = yaml.safe_load(f)
        event = json.loads(json_str)

        if "result" in event:

            # lexical_scores = {u'NOR': 0, u'MSA': 0, u'EGY': 0, u'LAV': 0, u'GLF': 0}
            # acoustic_scores = {u'NOR': 0.1, u'MSA': 0.225, u'EGY': 0.225, u'LAV': 0.225, u'GLF': 0.225}
            text = event['result']['hypotheses'][0]['transcript']
            segment_length = event['segment-length']
            tokens = text.strip().split()

            # print('transcript: ', text)
            token_list_10.add_tokens_list(tokens, event['id'])
            utterance = ' '.join(token_list_10.get_n_tokens())
            # lexical_scores = lexical_identification.identify_dialect(utterance)

            out_dir = r'/adi1/spool/asr/nnet3sac'
            raw_file_path = os.path.join(out_dir, 'audio', event['id'] + '.raw')
            debug_dir = os.path.join(out_dir, str(datetime.date.today()), event['id'])

            try:
                os.makedirs(debug_dir)
            except OSError as e:
                if not os.path.isdir(debug_dir):
                    raise

            a, b, c = str(time.time()).partition('.')
            time_stamp = ''.join([a, b, c.zfill(2)])
            raw_file_obj = open(raw_file_path, 'rb', os.O_NONBLOCK)

            # 16,000*2 byte for (1) sec
            # nBytes = SEC*framerate*samplewidth
            memory_buffer = BytesIO()
            with contextlib.closing(wave.open(memory_buffer, 'wb')) as wave_obj:
                wave_obj.setnchannels(1)
                wave_obj.setframerate(16000)
                wave_obj.setsampwidth(2)
                raw_file_obj.seek(0)
                wave_obj.writeframes(raw_file_obj.read())
            memory_buffer.flush()
            memory_buffer.seek(0)
            acoustic_scores = acoustic_identification4.dialect_estimation(memory_buffer)


            # lexical_weight = 0.3
            acoustic_weight = 1.0 #- lexical_weight
            # weighted_lexical = {dialect: value * lexical_weight for dialect, value in lexical_scores.items()}
            weighted_acoustic = {dialect: value * acoustic_weight for dialect, value in acoustic_scores.items()}

            # did_scores = {key: weighted_lexical[key] + weighted_acoustic[key] for key in [u'EGY', u'GLF', u'LAV',
            #                                                                               u'MSA', u'NOR']}

            did_scores = {key: weighted_acoustic[key] for key in
                          ['ALG', 'EGY', 'IRA', 'JOR', 'KSA', 'KUW', 'LEB', 'LIB', 'MAU', 'MOR', 'OMA',
                           'PAL', 'QAT', 'SUD', 'SYR', 'UAE', 'YEM']}
            # did_scores = {key: weighted_acoustic[key] for key in [u'ALG', u'EGY',u'IRA', u'JOR', u'KSA', u'KUW', u'LEB', u'LIB', u'MAU', u'MOR', u'OMA', u'PAL', u'QAT', u'SUD', u'SYR', u'UAE', u'YEM']}


            json_list = list()
            json_list.append(text)
            json_list.append(utterance)
            json_dict = {'acoustic_score': acoustic_scores, 'final_score': did_scores}
            # print(did_scores)
            # json_dict = {'lexical_score': lexical_scores, 'acoustic_score': acoustic_scores, 'final_score': did_scores}
            json_list.append(json_dict)
            text_file = os.path.join(debug_dir, time_stamp + '.json')
            with open(text_file, mode='w') as json_obj:
                json.dump(json_list, json_obj)
            logger.info("In post - 4")
            event['result']['hypotheses'].append(did_scores)


        return json.dumps(event)
    except:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.error("Failed to process JSON result: %s : %s " % (exc_type, exc_value))
        return str


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)8s %(asctime)s %(message)s ")

    lines = []
    while True:
        l = sys.stdin.readline()
        if not l: break  # EOF
        if l.strip() == "":
            if len(lines) > 0:
                result_json = post_process_json("".join(lines))
                print result_json
                print
                sys.stdout.flush()
                lines = []
        else:
            lines.append(l)

    if len(lines) > 0:
        result_json = post_process_json("".join(lines))
        print result_json
        lines = []
