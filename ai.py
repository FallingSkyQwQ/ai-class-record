import tkinter as tk
from tkinter import messagebox
import pyaudio
import wave
import requests
import threading

# 录音设置
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 60  # 最大录音时间10秒

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("AI课程日志")
        self.root.geometry("230x320")
        self.recording = False
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.init_ui()

    def init_ui(self):
        # 按钮
        self.btn_record = tk.Button(self.root, text="开始录音", command=self.start_record, 
                                   bg="#4CAF50", fg="white", font=("Arial", 12))
        self.btn_record.pack(pady=20)

        # 状态标签
        self.status_label = tk.Label(self.root, text="点击按钮开始录音", wraplength=200)
        self.status_label.pack(pady=10)

        # 结果文本框
        self.result_text = tk.Text(self.root, height=10, wrap=tk.WORD)
        self.result_text.pack(pady=10)

    def start_record(self):
        if not self.recording:
            self.recording = True
            self.btn_record.config(text="停止录音", bg="#f44336")
            self.status_label.config(text="正在录音...")
            self.frames = []
            self.stream = self.audio.open(format=FORMAT,
                                        channels=CHANNELS,
                                        rate=RATE,
                                        input=True,
                                        frames_per_buffer=CHUNK)
            threading.Thread(target=self.record).start()
        else:
            self.stop_record()

    def stop_record(self):
        self.recording = False
        self.btn_record.config(text="开始录音", bg="#4CAF50")
        self.stream.stop_stream()
        self.stream.close()
        self.stream = None
        self.save_record()
        self.status_label.config(text="录音结束，正在识别...")
        threading.Thread(target=self.process_audio).start()

    def record(self):
        while self.recording:
            data = self.stream.read(CHUNK)
            self.frames.append(data)

    def save_record(self):
        wf = wave.open("output.wav", 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def process_audio(self):
        # 语音识别部分
        # 使用百度语音识别API示例
        API_KEY = "JXUe5CJAEIDFVi9mIvNL24sk"
        API_KkEY = "JXUe5CJAEIDFVi9mIvNL24sk"
        SECRET_KEY = "yqRy1zeG3SoAABEM2IfxWwJF5vrzyrNc"
        
        with open("output.wav", "rb") as f:
            data = f.read()
        
        headers = {'Content-Type': 'audio/wav'}
        response = requests.post(f"http://vop.baidu.com/server_api?lm=3600&from=your_app",
                                 headers=headers, params={"cuid": "your_cuid", "token": API_KEY})
        
        if response.status_code == 200:
            text = response.text
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "识别结果:\n" + text)
            
            # AI概括部分
            client = OpenAI(
            api_key = "sk-UsTK1Zfjun20GXGnEcVDZfytayomOlI1gZSlJOnV0BS9SSQU",
            base_url = "https://api.moonshot.cn/v1",
         )
 
            completion = client.chat.completions.create(
            model = "moonshot-v1-8k",
            messages = [
            {"role": "system", "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。。"},
            {"role": "user", "content": "你好,概括以下内容 + text"}
            ],
             temperature = 0.3,
         )
 
            print(completion.choices[0].message.content)
            if summary_response.status_code == 200:
                summary = summary_response.json()["summary"]
                self.result_text.insert(tk.END, "\n\n概括结果:\n" + summary)
                
                # 推送到服务器
                self.push_to_server(summary)
        else:
            messagebox.showerror("错误", "语音识别失败")

    def push_to_server(self, text):
        # 将文本转换为URL编码
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        
        # 推送到服务器
        response = requests.get(f"https://sctapi.ftqq.com/SCT241745TFdvuyG62DamwAwnsiFVkQKb5.send?title=课程日志&despt={encoded_text}")
        if response.status_code == 200:
            self.status_label.config(text="成功推送到服务器")
        else:
            messagebox.showerror("错误", "推送失败")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()