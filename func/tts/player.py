# 播放器
import subprocess
from func.tools.singleton_mode import singleton
import pygame
import wave
import time


@singleton
class MpvPlay:

    def __init__(self):
        self.mixer = pygame.mixer
        self.mixer.init()
        # pass

    # 播放器播放
    def mpv_play(self, mpv_name, song_path, volume, start):
        # start：播放多少秒结束  volume：音量，最大100，最小0
        # subprocess.run(
        #     f'{mpv_name} -vo null --volume={volume} --start={start} "{song_path}" 1>nul',
        #     shell=True,
        # )
        dura = self.get_framerate_wave(song_path)
        music = self.mixer.Sound(song_path)
        music.play()
        time.sleep(dura)

    # 获取音频时长[秒]
    @staticmethod
    def get_framerate_wave(file_path):
        with wave.open(file_path, 'rb') as wav_file:
            frames = wav_file.getnframes()
            rate = wav_file.getframerate()
            dura = frames / float(rate)
            return dura
