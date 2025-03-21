import requests
import os
import random
import re
import argparse
from func.log.default_log import DefaultLog
from func.tools.string_util import StringUtil
from func.tools.singleton_mode import singleton
from func.gobal.data import VtuberData
from func.gobal.data import LLmData
from func.gobal.data import SingData
from func.gobal.data import TTsData

@singleton
class EasyAIVtuber:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    vtuberData = VtuberData()
    llmData = LLmData()  # llm数据
    singData = SingData()  # 唱歌数据
    ttsData = TTsData()  # 语音数据

    def __init__(self):
        pass

    def speak(self,speak_file):
        if speak_file:
            data = {
                "type": "speak",
                "speech_path": self.vtuberData.song_folder+speak_file
            }
            try:
                res = requests.post(f'{self.vtuberData.easyAIVtuberUrl}/alive', json=data)
                self.log.info(res.json())
            except Exception as e:
                self.log.info(f"【{self.vtuberData.easyAIVtuberUrl}/alive】信息回复异常")


    def rhythm(self,rhythm_file, rhythm_beat):
        if rhythm_file:
            data = {
                "type": "rhythm",
                "music_path": rhythm_file.name,
                "beat": rhythm_beat
            }
            res = requests.post(f'{self.vtuberData.easyAIVtuberUrl}/alive', json=data,timeout=(5,10))
            self.log.info(res.json())


    def sing(self,sing_file, sing_voice_file, sing_beat, sing_mouth):
        if sing_file and sing_voice_file:
            data = {
                "type": "sing",
                "music_path": self.vtuberData.song_folder+sing_file,
                "voice_path": self.vtuberData.song_folder+sing_voice_file,
                "beat": sing_beat,
                "mouth_offset": sing_mouth
            }
            try:
                res = requests.post(f'{self.vtuberData.easyAIVtuberUrl}/alive', json=data,timeout=(5,10))
                self.log.info(res.json())
            except Exception as e:
                self.log.info(f"【{self.vtuberData.easyAIVtuberUrl}/alive】信息回复异常")



    def stop(self):
        data = {
            "type": "stop",
        }
        try:
            res = requests.post(f'{self.vtuberData.easyAIVtuberUrl}/alive', json=data,timeout=(5,10))
            self.log.info(res.json())
        except Exception as e:
            self.log.info(f"【{self.vtuberData.easyAIVtuberUrl}/alive】信息回复异常")



    def change_img(self,img_path=None):
        if img_path:
            pass
        else:
            img_folder=self.vtuberData.img_folder
            imglist = os.listdir(img_folder)
            # 随机选择一张vtuber图片
            img_path = img_folder + r"/" + imglist[random.randint(1, len(imglist)) - 1]
        self.log.info(img_path)
        data = {
            "type": "change_img",
            "img": img_path
        }
        try:
            res = requests.post(f'{self.vtuberData.easyAIVtuberUrl}/alive', json=data,timeout=(5,10))
            self.log.info(res.json())
        except Exception as e:
            self.log.info(f"【{self.vtuberData.easyAIVtuberUrl}/alive】信息回复异常")


    # 换装入口处理
    def msg_deal_clothes(self, traceid, query, uid, user_name):
        text = ["变身"]
        num = StringUtil.is_index_contain_string(text, query)
        if num > 0:
            queryExtract = query[num: len(query)]  # 提取提问语句
            queryExtract = queryExtract.strip()
            queryExtract = re.sub("(。|,|，)", "", queryExtract)
            self.log.info(f"[{traceid}]变身提示：" + queryExtract)
            # 开始唱歌服装穿戴
            # self.emoteOper.emote_ws(1, 0, self.vtuberData.now_clothes)  # 解除当前衣服
            # self.emoteOper.emote_ws(1, 0, queryExtract)  # 穿上新衣服
            self.change_img()
            # self.vtuberData.now_clothes = queryExtract
            return True
        return False

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser()
#     parser.add_argument('--main_port', type=int, default=7888)
#     parser.add_argument('--webui_port', type=int, default=7999)
#     args = parser.parse_args()
#
#     support_audio_type = ["audio"]  # ".wav", ".mp3", ".flac"
#
#     with gr.Blocks() as demo:
#         with gr.Tab("说话"):
#             speak_file = gr.File(label="语音音频", file_types=support_audio_type)
#             speak_but = gr.Button("说话！！")
#             speak_but.click(speak, [speak_file])
#         with gr.Tab("摇"):
#             rhythm_file = gr.File(label="音乐音频", file_types=support_audio_type)
#             rhythm_beat = gr.Radio(["1", "2", "4"], value="2", label="节奏", info="越小点头频率越快")
#             rhythm_but = gr.Button("摇！")
#             rhythm_but.click(rhythm, [rhythm_file, rhythm_beat])
#         with gr.Tab("唱歌"):
#             with gr.Row():
#                 with gr.Column():
#                     sing_file = gr.File(label="原曲音频", file_types=support_audio_type)
#                 with gr.Column():
#                     sing_voice_file = gr.File(label="人声音频", file_types=support_audio_type)
#             sing_beat = gr.Radio(["1", "2", "4"], value="2", label="节奏", info="越小点头频率越快")
#             sing_mouth = gr.Slider(0, 1, value=0, step=0.1, label="嘴巴大小偏移", info="如果角色唱歌时的嘴张的不够大，可以试试将这个值设大")
#             sing_but = gr.Button("唱歌喵")
#             sing_but.click(sing, [sing_file, sing_voice_file, sing_beat, sing_mouth])
#         with gr.Tab("换皮"):
#             img = gr.Image(label="上传图片（512x512）", type="filepath", image_mode="RGBA")  # , height=300, width=300
#             change_but = gr.Button("启动！")
#             change_but.click(change_img, [img])
#
#         stop_but = gr.Button("停止当前动作")
#         stop_but.click(stop)
#
#     demo.launch(server_port=args.webui_port, inbrowser=True)
