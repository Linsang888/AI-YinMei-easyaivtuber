# 吟美Api web
import time
import uuid
import json
import os
import asyncio, aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from threading import Thread
from flask import Flask, jsonify, request, render_template
from flask_apscheduler import APScheduler

from func.obs.obs_websocket import VideoControl
from func.log.default_log import DefaultLog
from func.obs.obs_init import ObsInit
from func.vtuber.emote_oper import EmoteOper
from func.tts.tts_core import TTsCore
from func.llm.llm_core import LLmCore
from func.sing.sing_core import SingCore
from func.vtuber.action_oper import ActionOper
from func.draw.draw_core import DrawCore
from func.image.image_core import ImageCore
from func.search.search_core import SearchCore
from func.dance.dance_core import DanceCore
from func.cmd.cmd_core import CmdCore
from func.entrance.entrance_core import EntranceCore

from func.sing.lrc_init import LrcInit
from func.sing.websocket import WebSocketServer

from func.danmaku.blivedm.blivedm_core import BlivedmCore
from func.gobal.data import VtuberData
from func.gobal.data import CommonData
from func.gobal.data import SingData
from func.gobal.data import BiliDanmakuData


# 设置控制台日志
log = DefaultLog().getLogger()
# 重定向print输出到日志文件
def print(*args, **kwargs):
    log.info(*args, **kwargs)


commonData = CommonData()  #基础数据
Ai_Name = commonData.Ai_Name  # Ai名称


log.info("======================================")
log.warning(
    """                                                                                                                                      
                      ......                   .]]`         ,]].          
                     /@@@@@\                 =@@@@@^      ./@@@@@`        
   @@@@@@@@@@@      /@@@@@@@@.        ,]]]]]]]/@@@@@\]]]]]@@@@@@]]]]]]]]  
   @@@@@@@@@@@    ,@@@@@`@@@@@`       =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@  
   @@@@^ =@@@@   /@@@@@`  \@@@@@`     ,[[[[[[[[[[[[[\@@@@@[[[[[[[[[[[[[[  
   @@@@^ =@@@@ /@@@@@/ .]` =@@@@@@`     .]]]]]]]]]]]/@@@@@]]]]]]]]]]]]    
   @@@@^ =@@@@@@@@@@`\@@@@` .\@@@@@@\.  .@@@@@@@@@@@@@@@@@@@@@@@@@@@@@    
   @@@@^ =@@@@@@@@`   \@@@@`  ,\@@@@`   .[[[[[[[[[[[\@@@@@[[[[[[[[[[[[    
   @@@@^ =@@@@.@`      \@@@/.   .\@`  OOOOOOOOOOOOOOO@@@@@OOOOOOOOOOOOOO^ 
   @@@@^ =@@@@          .             @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@^ 
   @@@@^ =@@@@ O@@@@@@@@@@@@@@@@@^    [[[[[[[[[[[[[[\OOOOO[[[[[[[[[[[[[[` 
   @@@@^ =@@@@ O@@@@@@@@@@@@@@@@@^    ,]]]]]]]]]]]]]@@@@@\]]]]]]]]]]]]]]. 
   @@@@^ =@@@@             /@@@@@`    =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@. 
   @@@@@@@@@@@           ./@@@@@.     ,[[[[[[[[[[[@@@@@@@@@@[[[[[[[[[[[[. 
   @@@@@@@@@@@          ,@@@@@/                ]@@@@@@@\@@@@@@\`          
   @@@@^ =@@@@         =@@@@@/         .,]]O@@@@@@@@@/  ,@@@@@@@@@@@\]]]` 
                     ./@@@@@`         O@@@@@@@@@@@/`       [@@@@@@@@@@@@. 
                     ,[@@@@`          .@@@@@@O[`              .[O@@@@@@.  
                         ..                                                                                                               
"""
)

log.info(f"开始启动人工智能【{Ai_Name}】！")
log.info("源码地址：https://github.com/worm128/ai-yinmei")
log.info("整合包地址：https://www.bilibili.com/video/BV1zD421H76q/")
log.info("B站频道：程序猿的退休生活")
log.info("开发者：Winlone")
log.info("QQ群：27831318")

# 定时器
sched1 = AsyncIOScheduler(timezone="Asia/Shanghai")

# 1.b站直播间 2.api web
mode = commonData.mode

cmdCore = CmdCore()  #命令操作
entranceCore = EntranceCore()  #入口操作

# ============= B站直播间 =====================
blivedmCore = BlivedmCore()
# ============================================

# ============= api web =====================
app = Flask(__name__, template_folder="./html")
sched1 = APScheduler()
sched1.init_app(app)
# ============================================

# ============= Websocket =====================
# app2 = Flask(__name__)
# socketio = SocketIO(app2)
# lrc=LrcInit().get_ws()
# ============================================

# # ============= webui web =====================
# app2 = Flask(__name__, template_folder="./manage")
# sched2 = APScheduler()
# sched2.init_app(app2)
# # ============================================

# ============= OBS直播软件控制 ================
# obs直播软件连接
obs = ObsInit().get_ws()
# ============================================

# ============= LLM参数 =====================
llmCore = LLmCore()  # llm核心
# ============================================

# ============= 绘画参数 =====================
drawCore = DrawCore()
# ============================================

# ============= 搜图参数 =====================
imageCore = ImageCore()
# ============================================

# ============= 搜文参数 =====================
searchCore = SearchCore()
# ============================================

# ============= 唱歌参数 =====================
singCore = SingCore()  # 唱歌核心
# ============================================

# ============= 跳舞、表情视频 ================
danceCore = DanceCore()
# ============================================

# ============= 语音合成 =====================
ttsCore = TTsCore() # 语音核心
# ============================================

# ============= vtuber操作 =====================
vtuberData = VtuberData()  # vtuber数据
actionOper = ActionOper()  # 动作核心
emoteOper = EmoteOper() # 表情初始化
# ========================================

log.info("--------------------")
log.info("AI虚拟主播-启动成功！")
log.info("--------------------")
log.info("======================================")

# webui
# @app2.route("/", methods=["GET"])
# def index():
#     return render_template('index.html')

# 执行指令
@app.route("/cmd", methods=["GET"])
def http_cmd():
    cmdstr = request.args["cmd"]
    log.info(f'执行指令："{cmdstr}"')
    cmdCore.cmd("all",cmdstr,"0", "http_cmd")
    return jsonify({"status": "成功"})

# http说话复读【postman调用】
@app.route("/say", methods=["POST"])
def http_say():
    text = request.data.decode("utf-8")
    tts_say_thread = Thread(target=ttsCore.tts_say, args=(text,))
    tts_say_thread.start()
    return jsonify({"status": "成功"})

# http人物表情输出
@app.route("/emote", methods=["POST"])
def http_emote():
    data = request.json
    text = data["text"]
    emote_thread1 = Thread(target=emoteOper.emote_ws, args=(1, 0.2, text))
    emote_thread1.start()
    return jsonify({"status": "成功"})

# http唱歌接口处理【fastgpt调用】
@app.route("/http_sing", methods=["GET"])
def http_sing():
    songname = request.args["songname"]
    username = "所有人"
    singCore.http_sing(songname,username)
    return jsonify({"status": "成功"})

# http绘画接口处理【fastgpt调用】
@app.route("/http_draw", methods=["GET"])
def http_draw():
    drawname = request.args["drawname"]
    drawcontent = request.args["drawcontent"]
    username = "所有人"
    drawCore.http_draw(drawname,drawcontent,username)
    return jsonify({"status": "成功"})

# http更换场景
@app.route("/http_scene", methods=["GET"])
def http_scene():
    scenename = request.args["scenename"]
    actionOper.changeScene(scenename)
    return jsonify({"status": "成功"})


# http接口处理【postman接口调用】
@app.route("/msg", methods=["POST"])
def input_msg():
    data = request.json
    query = data["msg"]  # 获取弹幕内容
    uid = data["uid"]  # 获取用户昵称
    user_name = data["username"]  # 获取用户昵称
    traceid = str(uuid.uuid4())
    entranceCore.msg_deal(traceid, query, uid, user_name)
    return jsonify({"status": "成功"})


# 聊天回复弹框处理【html回复框回调】
@app.route("/chatreply", methods=["GET"])
def chatreply():
    CallBackForTest = request.args.get("CallBack")
    jsonStr = ttsCore.http_chatreply()
    if CallBackForTest is not None:
        jsonStr = CallBackForTest + jsonStr
    return jsonStr

# 聊天【用户funasr语音对话】
@app.route("/chat", methods=["POST", "GET"])
def chat():
    CallBackForTest = request.args.get("CallBack")
    uid = request.args.get("uid")
    username = request.args.get("username")
    text = request.args.get("text")
    # =========处理消息开始========
    status = "成功"
    traceid = str(uuid.uuid4())
    if text is None:
        jsonStr = "({\"traceid\": \"" + traceid + "\",\"status\": \"值为空\",\"content\": \"" + text + "\"})"
        return jsonStr
    # 消息处理
    entranceCore.msg_deal(traceid, text, uid, username)
    jsonStr = "({\"traceid\": \"" + traceid + "\",\"status\": \"" + status + "\",\"content\": \"" + text + "\"})"
    # =========end========
    if CallBackForTest is not None:
        jsonStr = CallBackForTest + jsonStr
    return jsonStr


# 点播歌曲列表
@app.route("/songlist", methods=["GET"])
def songlist():
    CallBackForTest = request.args.get("CallBack")
    jsonstr = singCore.http_songlist(CallBackForTest)
    if CallBackForTest is not None:
        jsonstr = CallBackForTest + jsonstr
    return jsonstr


def main():
    # 初始化衣服
    emoteOper.emote_ws(1, 0.2, "初始化")  # 解除当前衣服
    emoteOper.emote_ws(1, 0.2, "便衣")  # 穿上新衣服
    vtuberData.now_clothes = "便衣"

    # 跳舞表情
    # content = ""
    # for str in emote_list:
    #     content= content + str + ","
    # if content!="":
    #     obs.show_text("表情列表",content)

    # 停止所有视频播放
    obs.play_video("唱歌视频", "")
    obs.control_video("唱歌视频", VideoControl.STOP.value)
    obs.control_video("video", VideoControl.STOP.value)
    obs.control_video("表情", VideoControl.STOP.value)
    obs.play_video("伴奏", "")
    obs.control_video("伴奏", VideoControl.STOP.value)

    # 切换场景:初始化
    actionOper.init_scene()

    # 场景[白天黑夜]判断
    actionOper.check_scene_time()

    # 吟美状态提示:初始化清空
    obs.show_text("状态提示", "")

    if "blivedm" in mode or "api" in mode:
        # LLM回复
        sched1.add_job(func=llmCore.check_answer, trigger="interval", seconds=1, id="answer", max_instances=100)
        # tts语音合成
        sched1.add_job(func=ttsCore.check_tts, trigger="interval", seconds=1, id="tts", max_instances=1000)
        # 绘画
        sched1.add_job(func=drawCore.check_draw, trigger="interval", seconds=1, id="draw", max_instances=50)
        # 搜索资料
        sched1.add_job(func=searchCore.check_text_search, trigger="interval", seconds=1, id="text_search", max_instances=50)
        # 搜图
        sched1.add_job(func=imageCore.check_img_search, trigger="interval", seconds=1, id="img_search", max_instances=50)
        # 唱歌转换
        sched1.add_job(func=singCore.check_sing, trigger="interval", seconds=1, id="sing", max_instances=50)
        # 歌曲清单播放
        sched1.add_job(func=singCore.check_playSongMenuList, trigger="interval", seconds=1, id="playSongMenuList", max_instances=50)
        # 跳舞
        sched1.add_job(func=danceCore.check_dance, args=[sched1], trigger="interval", seconds=1, id="dance", max_instances=10)
        # 时间判断场景[白天黑夜切换]
        sched1.add_job(func=actionOper.check_scene_time, trigger="cron", hour="6,17,18", id="scene_time")
        # 欢迎语
        sched1.add_job(func=llmCore.check_welcome_room, trigger="interval", seconds=20, id="welcome_room", max_instances=50)
        sched1.start()


        # 开启web
        app_thread = Thread(target=apprun)
        app_thread.start()

        # 启动websocket server
        # websocket_thread = Thread(target=wsrun())
        # websocket_thread.start()
        asyncio.run(start_websocket())


        # 开启webui
        # app2_thread = Thread(target=apprun2)
        # app2_thread.start()

    # 可以监听多个弹幕平台
    if "blivedm" in mode:
        asyncio.run(blivedmCore.listen_blivedm_task())
    else:
        while True:
            time.sleep(10)
    log.info("结束")


# http服务
def apprun():
    # 禁止输出日志
    app.logger.disabled = True
    # 启动web应用
    app.run(host="0.0.0.0", port=commonData.port)

async def start_websocket():
    websocket_server = WebSocketServer()
    # 启动 WebSocket 服务器
    websocket_task = asyncio.create_task(websocket_server.start())
    singData = SingData()  # 唱歌数据
    lrc=LrcInit()
    # 定时向 WebSocket 客户端发送数据
    async def send_data_periodically():
        # 首次发送消息，与客户端建立链接
        data = {
            "type": "歌词",
            "status": "",
            "text": "",
            "next": "",
        }
        await asyncio.sleep(2)
        await websocket_server.send(json.dumps(data))
        while True:
            if singData.sing_play_flag == 1:
                lrc_path=vtuberData.song_folder+singData.SongNowPath+"song.lrc"
                log.info(f"lrc文件路径:{lrc_path}")
                if os.path.exists(f"{lrc_path}"):
                    dictmusic=lrc.get_music_dict(lrc_path)
                    data = {
                        "type": "歌词",
                        "status": "start",
                        "text": "",
                        "next": "",
                    }
                    await asyncio.sleep(2)
                    await websocket_server.send(json.dumps(data))

                    listmuscitime = []  # 创建空列表,把字典的key写进去
                    for keys in dictmusic.keys():
                        listmuscitime.append(keys)
                    listmuscitime.sort()  # 默认对列表进行升序
                    time.sleep(listmuscitime[0])
                    for index in range(len(listmuscitime)):
                        if index > 0:
                            time1=(listmuscitime[index]-listmuscitime[index-1])
                            text=dictmusic.get(listmuscitime[index])+"\n"  # 对列表里面的key值下标遍历,进而用get取字典的value
                            if index+1<len(listmuscitime):
                                next=dictmusic.get(listmuscitime[index+1])+"\n"
                            else:
                                next=""

                            if index==1:
                                status="start"
                            else:
                                status=""

                            data = {
                                "type": "歌词",
                                "status": status,
                                "text": text,
                                "next": next
                            }
                            # 判断是否切歌
                            if singData.sing_play_flag == 1:
                                await asyncio.sleep(time1)  # 两段歌词之间的时间
                                await websocket_server.send(json.dumps(data))
                            else:
                                data = {
                                    "type": "歌词",
                                    "status": "end",
                                    "text": text,
                                    "next": next
                                }
                                await websocket_server.send(json.dumps(data))
                    while singData.sing_play_flag == 1:
                        time.sleep(1)
                    data = {
                        "type": "歌词",
                        "status": "end",
                        "text": text,
                        "next": next
                    }
                    await websocket_server.send(json.dumps(data))
            else:
                time.sleep(1)

    periodic_task = asyncio.create_task(send_data_periodically())
    # 并发运行所有任务
    await asyncio.gather(websocket_task, periodic_task)

if __name__ == "__main__":
    main()
