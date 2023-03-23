import argparse
import pyaudio

import riva.client
from riva.client.argparse_utils import (
    add_asr_config_argparse_parameters,
    add_connection_argparse_parameters,
)

AUDIO_FORMAT = pyaudio.paInt16
AUDIO_CHANNELS = 1
AUDIO_RATE = 44100
AUDIO_CHUNK_SIZE = 1024


def stream_asr(config, chunk_size, audio_stream):
    auth = riva.client.Auth(uri="localhost:50051")
    asr_service = riva.client.ASRService(auth)
    riva.client.print_streaming(
        responses=asr_service.streaming_response_generator(
            audio_chunks=audio_stream,
            streaming_config=config,
        ),
        additional_info="time",
    )


def audio_stream(file_streaming_chunk):
    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=AUDIO_FORMAT,
        channels=AUDIO_CHANNELS,
        rate=AUDIO_RATE,
        input=True,
        frames_per_buffer=file_streaming_chunk,
    )

    print("Starting stream...")
    stream.start_stream()

    try:
        while stream.is_active():
            data = stream.read(file_streaming_chunk)
            yield data
    except KeyboardInterrupt:
        print("Interrupted by user")

    print("Stopping stream...")
    stream.stop_stream()
    stream.close()
    audio.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser = add_connection_argparse_parameters(parser)
    parser.add_argument("--output-file")
    parser.add_argument("--file-streaming-chunk", type=int, default=AUDIO_CHUNK_SIZE)
    parser = add_asr_config_argparse_parameters(
        parser, max_alternatives=True, profanity_filter=True, word_time_offsets=True
    )

    args = parser.parse_args()
    args.language_code = "ja-JP"

    config = riva.client.StreamingRecognitionConfig(
        config=riva.client.RecognitionConfig(
            encoding=riva.client.AudioEncoding.LINEAR_PCM,
            language_code=args.language_code,
            max_alternatives=args.max_alternatives,
            profanity_filter=args.profanity_filter,
            enable_automatic_punctuation=args.automatic_punctuation,
            verbatim_transcripts=not args.no_verbatim_transcripts,
            enable_word_time_offsets=args.word_time_offsets,
            sample_rate_hertz=AUDIO_RATE,
            audio_channel_count=AUDIO_CHANNELS,
        ),
        interim_results=True,
    )
    riva.client.add_word_boosting_to_config(
        config, args.boosted_lm_words, args.boosted_lm_score
    )

    stream_asr(
        config, args.file_streaming_chunk, audio_stream(args.file_streaming_chunk)
    )
