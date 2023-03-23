# NVIDIA Riva Speech APIによる音声認識のテスト

## ファイルを入力とする

```
python ./file_client.py --input-file output.wav --language-code ja-JP 
```

## マイク入力をストリーミングで認識する

```
python ./stream_client.py --language-code ja-JP
```


## 認識結果を GPT-3.5-turbo になげて修正してもらう

User Message:

```
ソフトウェア開発についての会話を音声認識で文字起こししています。以下の文章が文字起こしされたものですが、不自然な部分を、ソフトウェア開発のコンテキストという前提のもとに修正してください。出力は、修正した文字列だけにしてください。

入力：パイソンでフラスコンヘヴアプリケーションが作りたいです
出力:
```

ChatGPT returns:

```
「PythonでFlaskアプリケーションを作りたいです。」
```
