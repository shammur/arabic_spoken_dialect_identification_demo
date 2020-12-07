# Arabic Dialect Identification Model Usage

The repository includes examples of how to run acoustic ADI model for real-time usage.
The folders include examples used for a basic api and for online ADI demo - integrated with a kaldi based ASR

For simplicity, we provide a notebook showing how to use the acoustic model for automatic prediction
Shared Colab notebook: 

https://colab.research.google.com/drive/10lbKWAvnlROe7_K-dgJGSykGQxpyLbq6?usp=sharing


Acoustic models are located in : arabic_spoken_dialect_identification_demo/dialectid_api/arabic_dialect_identification/acoustic/model



Dir:

dialectid-website/ -- includes the demo interface in https://dialectid.qcri.org/

qmdis-post-processor-full/ the post processing script ASR called when predicting ADI

dialectid_api/ an example of use of ADI model in API call


Instruction to run the demo in server:
how to start server** 

``
bash qmdis-server_cmd.sh
``

run workers:

``
qmdis-worker.sh
``

#Related Links

demo: https://dialectid.qcri.org/

demo link (YT): https://www.youtube.com/watch?v=IN2binq_Ei4&t=229s

git repo for farspeech2: https://github.com/KazBrekker1/FarSpeech.git

demo for farspeech2:





