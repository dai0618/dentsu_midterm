import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import whisper
from whisper import Whisper

# MODEL_TYPE = "large"  # NOTE: too much time to take for loading
MODEL_TYPE = "small"
REMOVE_MDOEL_INSTANCE_EVERY_GEN = False
model: Optional[Whisper] = None  # cache  model instance

os.makedirs("./text_file", exist_ok=True)

def get_time():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def init_load_model():
    global model
    model = whisper.load_model(
        MODEL_TYPE,
        device="cpu"  # NOTE: 初期化時にGPUに乗るのを防ぐ
    )
    model.half()  # NOTE: 学習済重みを変換 fp32->fp16
    for m in model.modules():
        if isinstance(m, whisper.model.LayerNorm):
            m.float()


def speech_to_text(audio_file: str) -> Optional[str]:
    """Speech to text conversion with Whisper transcription.

    arg: path to audio file
    returns: path to transcription text file, if failed returns None
    """
    global model
    # try:
    if model is None:            
        model = whisper.load_model(MODEL_TYPE, device="cpu")
        # model.half()

    # model.to("cuda")
    result = model.transcribe(
        audio_file,
        language="japanese",
        fp16=True  # NOTE: fp16で推論する
    )
    result_txt = result["text"]
    print(result_txt)
    save_file_path = Path(f"{os.getcwd()}/text_file/{get_time()}.txt")
    with open(save_file_path, 'w', encoding="utf-8_sig") as f:
        f.write(result_txt)
    return result_txt
    # except:
    #     print("error occured at whisper")
