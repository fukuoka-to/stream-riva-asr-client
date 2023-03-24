# NVIDIA Riva ASRによる音声認識

## 事前準備

NVIDIA Riva ASRのサーバーがローカルで起動している必要があります。

```shell
bash riva_start.sh
```


## ファイルを入力とする

```shell
python ./asr_file_client.py --input-file sample.wav
```

## マイク入力をストリーミングで音声認識する

```shell
python ./asr_stream_client.py
```
