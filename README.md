# NVIDIA Riva Speech APIによる音声認識のテスト

## ファイルを入力とする

```
python ./file_client.py --input-file output.wav
```

## マイク入力をストリーミングで認識する

```
python ./stream_client.py --language-code ja-JP
```
