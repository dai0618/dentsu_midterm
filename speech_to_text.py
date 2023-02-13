import os
import time
from pythonosc import dispatcher
from pythonosc import osc_server
from pythonosc import udp_client

from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder

import threading
from typing import Any, Callable, Dict, List, Optional, Union

from pythonosc import udp_client
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from speech_recognition import speech_to_text

import whisper

count_index = 0

class OSCServer:
    def __init__(self, ip: str, port: int) -> None:
        # addresses
        self.address_0 = "/speech_recognition/0"
        self.address_1 = "/speech_recognition/1"
        self.address_fuga = "/example_fuga"
        self.address_piyo = "/example_piyo"
        # callback functions
        self.on_received_0: Optional[Callable] = None
        self.on_received_1: Optional[Callable] = None
        self.on_received_fuga: Optional[Callable] = None
        self.on_received_piyo: Optional[Callable] = None
        self.server: Optional[BlockingOSCUDPServer] = None
        self.ip = ip
        self.port = port

    def parse_message(self, input_args: str) -> List[str]:
        if type(input_args) == float:
            args = [input_args]
        else:
            args: List[str] = input_args.split(" ")
        return args

    def run(self, single_thread=False) -> None:
        """Start OSC server on main or sub thread.

        Args:
            single_thread (bool, optional): Defaults to False.
        """
        self.dispatcher = Dispatcher()

        if self.on_received_0:
            self.dispatcher.map(self.address_0,
                                self.on_received_0)  # type: ignore
        # NOTE: 受け付けるアドレスを増やしたい場合は以下のようにしてアドレスを増やす
        if self.on_received_1:
            self.dispatcher.map(self.address_1,
                                self.on_received_1)  # type: ignore
        if self.on_received_fuga:
            self.dispatcher.map(self.address_fuga,
                                self.on_received_fuga)  # type: ignore
        if self.on_received_piyo:
            self.dispatcher.map(self.address_piyo,
                                self.on_received_piyo)  # type: ignore

        self.server = BlockingOSCUDPServer(
            (self.ip, self.port), self.dispatcher)
        print(f"Serving on {self.server.server_address}")
        if single_thread:
            self.server.serve_forever()
        else:
            # running the server on new thread
            server_thread = threading.Thread(target=self.server.serve_forever)
            server_thread.start()

    def stop(self):
        if self.server is not None:
            self.server.shutdown()

    def __del__(self):
        if self.server is not None:
            self.server.shutdown()


class OSCSender:
    def __init__(self, ip: str, port: int) -> None:
        self.client = udp_client.SimpleUDPClient(ip, port)
        # NOTE: 一つのSenderに付き送れるホストは一つ。
        self.ip = ip
        self.port = port

    def send(self, path: str, msg: Any) -> None:
        assert path[0] == "/", "given osc address path is incorrect"
        print(f"sending OSC message",
              f"(type={type(msg)})",
              f"to {self.ip}:{self.port}:{path}")
        self.client.send_message(path, msg)

    def __del__(self):
        if self.client is not None:
            del self.client


def get_sample_callback(sender: OSCSender, keyword: str = "") -> Callable:
    """Callback関数を返す関数

    Args:
        sender (OSCSender): 受信時にオウム返しをするのでClientのインスタンスが必要
        keyword (str, optional): hoge/fuga/piyo 等のアドレスのときどうするかみたいな.

    Returns:
        Callable: 関数を返す
    """

    # NOTE: もし機械学習モデル等を読む場合は、`get_sample_callback`の引数でパスを受け取り
    # ここでインスタンスの読み込みを行うことで、毎回の呼び出しでの読み込みなどが発生せずに済む
    # 例) model = Model.load_model(given_path)

    def callback_func(addr: str, *args: Any):
        global count_index
        """Actual callback function: 実際にOSCを受け取って呼ばれる関数

        Args:
            addr (str): OSCのパス (e.g. /path/to)
            args (Any): 可変長引数なのでTupleとして扱うこと
        """

        # NOTE: ここで処理を行う。
        # 例) res = model.generate(type=args[0])
        #     res.save_image("/generated/path.png")
        #     sender.send("/generated_result", "/generated/path.png")

        if keyword != "":
            print(keyword, "!!!!")
        print("received:", addr, args)
        
        #audioファイルのパスを受信し文字起こしを開始。
        audio_file_path = args[0].replace("Macintosh HD:","")
        time.sleep(1)
        # audio_file_path = args[0].replace("Macintosh HD:","")　#macのみ必要

        if addr=="/speech_recognition/0":      
            if os.path.isfile(audio_file_path):
                if args[0].endswith(".wav"):
                    count_index += 1
                    print("audio file path:", audio_file_path)
                    result_text = speech_to_text(audio_file_path)
                    count_num = str(result_text).count("わん") + str(result_text).count("ワン") + str(result_text).count("One")
                    print(count_num)
                    if count_num >= 6:
                        print("2マス進みます")
                        send_num = 6
                    elif 1 <= count_num <= 5:
                        print("1マス進みます")
                        send_num = count_num
                    else:
                        print("1マス戻る")
                        send_num = 0
                    address_state = "/start_unity/0"
                    sender.send(address_state,send_num) # state machineにtextファイルのパスを送信。
                else:
                    print("incorrect path:", args[0])
            else:
                print("file is not found!!")

        if addr=="/speech_recognition/1":
            print("audio_file_is",audio_file_path)       
            if os.path.isfile(audio_file_path):
                if args[0].endswith(".wav"):
                    print("audio file path:", audio_file_path)
                    result_text = speech_to_text(audio_file_path)
                    count_num = result_text.count("にゃ") + result_text.count("ニャ")
                    print(count_num)
                    if count_num >= 6:
                        print("2マス進みます")
                        send_num = 6
                    elif 1 <= count_num <= 5:
                        print("1マス進みます")
                        send_num = count_num
                    else:
                        print("1マス戻る")
                        send_num = 0
                    address_state = "/start_unity/1"
                    sender.send(address_state,send_num) # state machineにtextファイルのパスを送信。
                else:
                    print("incorrect path:", args[0])
            else:
                print("file is not found!!")

    return callback_func


if __name__ == "__main__":
    model = whisper.load_model("small", device="cpu")
    result = model.transcribe(
        "./recording_folder/sample.wav",
        language="japanese",
        fp16=True  # NOTE: fp16で推論する
    )
    server = OSCServer("127.0.0.1", 7773)
    sender = OSCSender("127.0.0.1", 6665)
    server.on_received_0 = get_sample_callback(sender)
    server.on_received_1 = get_sample_callback(sender)
    server.run(single_thread=True)