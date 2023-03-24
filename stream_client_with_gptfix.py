import io
from dataclasses import dataclass, asdict
from dotenv import DotEnv

import openai
import riva.client
from asr_stream_client import audio_stream, asr_config


SYSTEM_PROMPT_1 = """
あなたはネイティブの日本語の話者です。

- 音声認識によって文字起こしされたテキストを渡すので、自然な日本語に修正してください。
- 修正したテキストだけを出力してください
- それ以外の余計なテキストは出力しないこと

I will provide input in the following format:
input: [user text]

Please format the output as follows:
output: [your text]
"""

SYSTEM_PROMPT_2 = """
You are a native Japanese speaker.

- I will provide you with a partially incomplete text transcribed by voice recognition, please correct it to natural Japanese.
- The conversation is mainly about software development, so English words may be incorrect. Please guess and correct the words with high probability.
- In the Japanese context, words that are generally described in English should be written in English.
Please output only the corrected text.
- Do not output any unnecessary text.

I will provide input in the following format:
input: [user text]

Please format the output as follows:
output: [your text]
"""


class ChatAPI:
    MODEL_MAP = {
        "gpt-3.5-turbo-0301": "gpt-3.5-turbo",
        "gpt-4-0314": "gpt-4",
        "gpt-4-32k-0314": "gpt-4-32k",
    }

    MAX_TOKENS = {
        "gpt-3.5-turbo": 4096,
        "gpt-4": 8192,
        "gpt-4-32k": 32768,
    }

    class APIError(openai.OpenAIError):
        def __init__(self, args, **kargs):
            super().__init__(args, kargs)

    @dataclass
    class ChatResponse:
        id: str
        role: str
        content: str
        finish_reason: str
        prompt_tokens: int
        completion_tokens: int

        def to_dict(self):
            return asdict(self)

    def __init__(self, api_key: str, model: str = "gpt-4", temperature: float = 0.2):
        openai.api_key = api_key
        self._model = model
        self._chat_api = None
        self._system_prompt = SYSTEM_PROMPT_1
        self._temperature = temperature

    def call(self, model: str, messages: list[dict]) -> ChatResponse:
        model = ChatAPI.MODEL_MAP.get(model, model)
        max_tokens = int(ChatAPI.MAX_TOKENS[model] / 3)

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=self._temperature,
            max_tokens=max_tokens,
            timeout=5,
        )

        prompt_tokens = response["usage"]["prompt_tokens"]
        completion_tokens = response["usage"]["completion_tokens"]

        response_message = response["choices"][0]["message"]
        return ChatAPI.ChatResponse(
            id=response["id"],
            role=response_message["role"],
            content=response_message["content"],
            finish_reason=response["choices"][0]["finish_reason"],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def fix_text(self, text):
        messages = [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": f"input: {text}"},
        ]
        response = self.call(self._model, messages)
        return response.content


class ResponseProcessor(io.StringIO):
    def __init__(self, chat_api: ChatAPI):
        super().__init__()
        self._chat_api = chat_api

    def write(self, text: str):
        print(text, end="")
        if not text.startswith(">>>"):
            last_text = text.split(":")[2].strip()
            if len(last_text) > 0:
                fixed_text = self._chat_api.fix_text(last_text)
                print("GPT response:", fixed_text)


def stream_asr(config, audio_stream, output=None):
    auth = riva.client.Auth(uri="localhost:50051")
    asr_service = riva.client.ASRService(auth)
    riva.client.print_streaming(
        responses=asr_service.streaming_response_generator(
            audio_chunks=audio_stream, streaming_config=config
        ),
        output_file=output,
        additional_info="time",
    )


if __name__ == "__main__":
    env = DotEnv()
    if not env.has("OPENAI_API_KEY"):
        raise ValueError("Please set variable OPENAI_API_KEY in .env")

    chat_api = ChatAPI(env.get("OPENAI_API_KEY"))
    response_processor = ResponseProcessor(chat_api)

    args, config = asr_config()

    stream_asr(
        config=config,
        audio_stream=audio_stream(args.file_streaming_chunk),
        output=response_processor,
    )
