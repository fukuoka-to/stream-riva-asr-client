import argparse

import riva.client
from riva.client.argparse_utils import (
    add_asr_config_argparse_parameters,
    add_connection_argparse_parameters,
)


def send_file(
    config,
    input_file,
    output_file,
    file_streaming_chunk,
    word_time_offsets,
):
    auth = riva.client.Auth(uri="localhost:50051")
    asr_service = riva.client.ASRService(auth)

    with riva.client.AudioChunkFileIterator(
        input_file,
        file_streaming_chunk,
        delay_callback=riva.client.sleep_audio_length,
    ) as audio_chunk_iterator:
        riva.client.print_streaming(
            responses=asr_service.streaming_response_generator(
                audio_chunks=audio_chunk_iterator,
                streaming_config=config,
            ),
            # output_file=None,
            additional_info="time",
            # word_time_offsets=word_time_offsets,
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser = add_connection_argparse_parameters(parser)
    parser.add_argument("--input-file", required=True)
    parser.add_argument("--output-file")
    parser.add_argument("--file-streaming-chunk", type=int, default=1600)
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
        ),
        interim_results=True,
    )

    riva.client.add_audio_file_specs_to_config(config, args.input_file)
    riva.client.add_word_boosting_to_config(
        config, args.boosted_lm_words, args.boosted_lm_score
    )

    send_file(
        config,
        args.input_file,
        args.output_file,
        args.file_streaming_chunk,
        args.word_time_offsets,
    )
