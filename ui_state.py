import os
from flask import Flask, request, redirect, url_for, render_template
from flask import send_from_directory
from pythonosc import udp_client
from pythonosc.osc_message_builder import OscMessageBuilder
import time
import whisper
import pandas as pd

app = Flask(__name__)
index_num = 0

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/thanks")
def thanks():
    return render_template("thanks.html")

@app.route("/rec0", methods=['GET', 'POST'])
def rec0():
    global index_num
    df = pd.read_csv('./static/talk_topic.csv')
    topic = df["topic"][index_num]
    client1 = udp_client.UDPClient('127.0.0.1', 9998)
    msg = OscMessageBuilder(address="/topic")
    msg.add_arg(topic)
    m = msg.build()
    client1.send(m)
    if request.method == 'POST':
        client0 = udp_client.UDPClient('127.0.0.1', 8888)
        client1 = udp_client.UDPClient('127.0.0.1', 9998)
        msg = OscMessageBuilder(address="/start")
        msg.add_arg("0")
        m = msg.build()
        client0.send(m)
        client1.send(m)
        time.sleep(30)
        msg = OscMessageBuilder(address="/stop")
        msg.add_arg("0")
        m = msg.build()
        client0.send(m)
        client1.send(m)
        index_num+=1
    return render_template("recording-0.html")

@app.route("/rec1", methods=['GET', 'POST'])
def rec1():
    if request.method == 'POST':
        client0 = udp_client.UDPClient('127.0.0.1', 8888)
        client1 = udp_client.UDPClient('127.0.0.1', 9998)
        msg = OscMessageBuilder(address="/start")
        msg.add_arg("1")
        m = msg.build()
        client0.send(m)
        client1.send(m)
        time.sleep(30)
        msg = OscMessageBuilder(address="/stop")
        msg.add_arg("1")
        m = msg.build()
        client0.send(m)
        client1.send(m)
    return render_template("recording-1.html")

if __name__ == "__main__":
    whisper.load_model(
        "small",
        device="cpu"  # NOTE: 初期化時にGPUに乗るのを防ぐ
    )
    app.debug = True
    app.run(host='0.0.0.0', port=2000) 