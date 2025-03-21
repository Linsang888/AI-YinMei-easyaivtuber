import os

from func.log.default_log import DefaultLog
from func.config.default_config import defaultConfig
from func.sing.websocket import WebSocketServer
from func.tools.singleton_mode import singleton
from func.gobal.data import SingData
import json
import time
import asyncio

@singleton
class LrcInit:
    # 设置控制台日志
    log = DefaultLog().getLogger()
    # 加载配置
    config = defaultConfig().get_config()

    def __init__(self):
        pass

    @staticmethod
    def get_music_dict(lrcfile):
        file = open(lrcfile, "r", encoding="utf-8")
        musiclrc=file.read()
        file.close()
        """获得歌词字典

        :param musiclrc: 歌词字符串
        :return: 时间与歌词对应的字典
        """
        dictmusic = {}  # 创建一个空字典，用来装 时间(key) 和 歌词(value)
        listline1 = musiclrc.splitlines()  # 安照行进行切割 把每一行变成列表的一个元素

        for i in listline1:  # 把每一行元素遍历出来，准备切割

            listline2 = i.split("]")  # 以 ] 为切割符
            value = listline2[-1]  # 每一次遍历 把歌词元素(每一次遍历都是最后一个) 赋值给 value

            for j in range(len(listline2)-1):  # 遍历 listLine2  len(listLine2)-1 除去最后的非时间字符串(歌词)

                keymusic = listline2[j][1:]  # [1:]从索引值为1开始取目的是除去 [
                # keymusic = listline2[j].strip()[1:]  # [1:]从索引值为1开始取目的是除去 [ 如果有缩进的话 需要用strip()去除空格  方案二

                keytime = keymusic.split(":")  # 对遍历的的时间字符串以冒号进行切割

                musictime = float(keytime[0])*60+float(keytime[1])  # 计算出每个时间的总秒数

                key = musictime  # 把时间赋值给字典中的 key

                dictmusic[key] = value  # 把value 赋值给对应的时间 key
        # print(dictmusic)

        return dictmusic
