import os, sys
import numpy as np
import librosa
import soundfile as sf
import tensorflow as tf
from io import BytesIO
import wave
import contextlib
try:
    from ..utils import e2e_model_adi17 as nn_model_foreval
except:
    from arabic_dialect_identification.utils import e2e_model_adi17 as nn_model_foreval

# dialects = [u'EGY', u'GLF', u'LAV', u'MSA', u'NOR']
# dialects = [u'ALG', u'EGY',u'IRA', u'JOR', u'KSA', u'KUW', u'LEB', u'LIB', u'MAU', u'MOR', u'OMA', u'PAL', u'QAT', u'SUD', u'SYR', u'UAE', u'YEM']
dialects = ['ALG', 'EGY','IRA', 'JOR', 'KSA', 'KUW', 'LEB', 'LIB', 'MAU', 'MOR', 'OMA', 'PAL', 'QAT', 'SUD', 'SYR', 'UAE', 'YEM']

def cmvn_slide(feat ,winlen=300 ,cmvn=False):  # feat : (length, dim) 2d matrix
    # function for Cepstral Mean Variance Nomalization

    maxlen = np.shape(feat)[0]
    new_feat = np.empty_like(feat)
    cur = 1
    leftwin = 0
    rightwin = int(winlen /2)  # modified by shammur

    # middle
    for cur in range(maxlen):
        cur_slide = feat[cur -leftwin:cur +rightwin ,:]
        # cur_slide = feat[cur-winlen/2:cur+winlen/2,:]
        mean =np.mean(cur_slide, axis=0)
        std = np.std(cur_slide, axis=0)
        if cmvn == 'mv':
            new_feat[cur, :] = (feat[cur, :] - mean) / std  # for cmvn
        elif cmvn == 'm':
            new_feat[cur, :] = (feat[cur, :] - mean)  # for cmn
        if leftwin < winlen / 2:
            leftwin += 1
        elif maxlen - cur < winlen / 2:
            rightwin -= 1
    return new_feat


def feat_extract(y, sr, feat_type, n_fft_length=512, hop=160, vad=True, cmvn=False, exclude_short=500):
    # function for feature extracting

    feat = []
    utt_shape = []
    new_utt_label = []
    # for index, wavname in enumerate(filelist):
    #     # read audio input
    #     # print(wavname)
    #     y, sr = librosa.core.load(wavname, sr=16000, mono=True, dtype='float')

    # extract feature
    if feat_type == 'melspec':
        Y = librosa.feature.melspectrogram(y, sr, n_fft=n_fft_length, hop_length=hop, n_mels=40, fmin=133,
                                           fmax=6955)
    elif feat_type == 'mfcc':
        Y = librosa.feature.mfcc(y, sr, n_fft=n_fft_length, hop_length=hop, n_mfcc=40, fmin=133, fmax=6955)
    elif feat_type == 'spec':
        Y = np.abs(librosa.core.stft(y, n_fft=n_fft_length, hop_length=hop, win_length=400))
    elif feat_type == 'logspec':
        Y = np.log(np.abs(librosa.core.stft(y, n_fft=n_fft_length, hop_length=hop, win_length=400)))
    elif feat_type == 'logmel':
        Y = np.log(librosa.feature.melspectrogram(y, sr, n_fft=n_fft_length, hop_length=hop, n_mels=40, fmin=133,
                                                  fmax=6955))
        # print(Y.shape)

    Y = Y.transpose()
    # print(Y.shape)

    # Simple VAD based on the energy
    if vad:
        E = librosa.feature.rmse(y, frame_length=n_fft_length, hop_length=hop, )
        # '''librosa change log for .7.0 >> (Root mean square error (rmse) has been renamed to rms)'''
        # E = librosa.feature.rmse(y, frame_length=n_fft_length,hop_length=hop,)
        threshold = np.mean(E) / 2 * 1.04
        vad_segments = np.nonzero(E > threshold)
        if vad_segments[1].size != 0:
            Y = Y[vad_segments[1], :]

    # exclude short utterance under "exclude_short" value
    # print(Y.shape[0], Y.shape)
    if exclude_short == 0 or (Y.shape[0] > exclude_short):
        if cmvn:
            Y = cmvn_slide(Y, 300, cmvn)
        # print('Y',Y.shape)
        feat.append(Y)
        utt_shape.append(np.array(Y.shape))
        # print('ut_shape',len(utt_shape))
        #             new_utt_label.append(utt_label[index])
        # sys.stdout.write('%s\r' % index)
        # sys.stdout.flush()

    # if index == 0:
    #     break

    tffilename = feat_type + '_fft' + str(n_fft_length) + '_hop' + str(hop)
    if vad:
        tffilename += '_vad'
    if cmvn == 'm':
        tffilename += '_cmn'
    elif cmvn == 'mv':
        tffilename += '_cmvn'
    if exclude_short > 0:
        tffilename += '_exshort' + str(exclude_short)

    return feat, new_utt_label, utt_shape, tffilename  # feat : (length, dim) 2d matrix



# Feature extraction configuration
INPUT_DIM = 40
IS_BATCHNORM = False
IS_TRAINING = False

softmax_num = 17

#init placeholder
x = tf.placeholder(tf.float32, [None,None,40])
y = tf.placeholder(tf.int32, [None])
s = tf.placeholder(tf.int32, [None,2])

emnet_validation = nn_model_foreval.nn(x,y,y,s,softmax_num,IS_TRAINING,INPUT_DIM,IS_BATCHNORM);

# sess = tf.InteractiveSession()
sess4 = tf.Session()
saver4 = tf.train.Saver()
# tf.initialize_all_variables().run()
sess4.run(tf.global_variables_initializer())

### Loading neural network
current_directory = os.path.dirname(os.path.abspath(__file__))
model_directory = os.path.join(current_directory, 'model')
model_path4 = os.path.join(model_directory, 'model7712000.ckpt-7712000')
saver4.restore(sess4,model_path4)



def softmax(x):
    """Compute softmax values for each sets of scores in x."""
    return np.exp(x) / np.sum(np.exp(x), axis=0)


def dialect_estimation(bytesIO_buffer):
    data, sample_rate = sf.read(bytesIO_buffer)
    # feat_tools.feat_extract('filename.wav','mdcc',400,160,True,'m',0)
    FEAT_TYPE = 'mfcc'
    N_FFT = 400
    HOP = 160
    VAD = True
    CMVN = 'm'
    EXCLUDE_SHORT = 0
    feat, utt_label, utt_shape, tffilename = feat_extract(data, sample_rate, FEAT_TYPE, N_FFT, HOP, VAD, CMVN, EXCLUDE_SHORT)
    likelihood = emnet_validation.o1.eval({x: feat, s: utt_shape}, session=sess4)

    probabilities = softmax(likelihood.ravel().tolist())

    return dict(zip(dialects, probabilities))


# def dialect_estimationWav(data):
#
#     # feat_tools.feat_extract('filename.wav','mdcc',400,160,True,'m',0)
#     FEAT_TYPE = 'mfcc'
#     N_FFT = 400
#     HOP = 160
#     VAD = True
#     CMVN = 'm'
#     EXCLUDE_SHORT = 0
#     sample_rate=16000
#     feat, utt_label, utt_shape, tffilename = feat_extract(data, sample_rate, FEAT_TYPE, N_FFT, HOP, VAD, CMVN, EXCLUDE_SHORT)
#     likelihood = emnet_validation.o1.eval({x: feat, s: utt_shape}, session=sess4)
#
#     probabilities = softmax(likelihood.ravel().tolist())
#
#     return dict(zip(dialects, probabilities))


def do_shuffle(feat, utt_label, utt_shape):
    #### shuffling
    shuffleidx = np.arange(0, len(feat))
    np.random.shuffle(shuffleidx)

    feat = np.array(feat)
    utt_label = np.array(utt_label)
    utt_shape = np.array(utt_shape)

    feat = feat[shuffleidx]
    utt_label = utt_label[shuffleidx]
    utt_shape = utt_shape[shuffleidx]

    feat = feat.tolist()
    utt_label = utt_label.tolist()
    utt_shape = utt_shape.tolist()

    return feat, utt_label, utt_shape
