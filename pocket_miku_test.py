#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pocket miku(midi) test

import copy
import time
import pygame
import pygame.midi

INSTURUMENT = 0  # miku，他の数字だと楽器

# exclusive data
EXCLUSIVE_FIRST = [0xF0, 0x43, 0X79, 0x09, 0x11, 0x0A, 0x00]
EXCLUSIVE_LAST = [0xF7]

def get_character_table():
    """ ポケットミクのデフォルトの文字テーブルを返す． """
    
    character = u'''あ い う え お
                    か き く け こ
                    が ぎ ぐ げ ご
                    きゃ きゅ きょ
                    ぎゃ ぎゅ ぎょ
                    さ すぃ す せ そ
                    ざ ずぃ ず ぜ ぞ
                    しゃ し しゅ しぇ しょ
                    じゃ じ じゅ じぇ じょ
                    た てぃ とぅ て と
                    だ でぃ どぅ で ど
                    てゅ でゅ
                    ちゃ ち ちゅ ちぇ ちょ
                    つぁ つぃ つ つぇ つぉ
                    な に ぬ ね の
                    にゃ にゅ にょ
                    は ひ ふ へ ほ
                    ば び ぶ べ ぼ
                    ぱ ぴ ぷ ぺ ぽ
                    ひゃ ひゅ ひょ
                    びゃ びゅ びょ
                    ぴゃ ぴゅ ぴょ
                    ふぁ ふぃ ふゅ ふぇ ふぉ
                    ま み む め も
                    みゃ みゅ みょ
                    や ゆ よ
                    ら り る れ ろ
                    りゃ りゅ りょ
                    わ うぃ うぇ うぉ ん'''.strip().split()

    character_table = dict([(text, i) for i, text in enumerate(character)])

    # 特殊音の追加
    character_table.update(dict([(text, i) for i, text in
                           enumerate(u'づぁ づぃ づ づぇ づぉ'.split(), 0x1A)]))
    character_table.update(dict([(text, i) for i, text in
                           enumerate(u'ゐ ゑ を N\\ m N J n'.split(), 0x78)]))

    return character_table

def midi_setup(insturument=0):
    """
    MIDIを扱うためのセットアップ関数．
    
    Inputs
    ----------
    instrument : int (default=0)
        演奏に用いる楽器．デフォルトは0:ミク
    
    Returns
    ----------
    midi_output : object
        pygamesのMIDI出力を扱うオブジェクト
    """
    
    # Pygamesの初期化
    pygame.init()
    pygame.midi.init()
    
    # 出力デバイスにポケットミクを指定
    for i in range(pygame.midi.get_count()):
        interf, name, input_dev, output_dev, opened = pygame.midi.get_device_info(i)
        if output_dev and b'NSX-39 ' in name:
            print('NSX-39 port number is ' + str(i))
            midi_output = pygame.midi.Output(i)

    midi_output.set_instrument(insturument)  # 楽器を指定

    return midi_output

def get_midi_phrases(text, character_table):
    """
    歌詞をポケットミクが扱う16進数文字列に変換する関数．
    
    Inputs
    ----------
    text : str
        歌詞(半角スペースで区切られていてもよい)
    character_table : dict(str:str)
        ポケットミクのデフォルトの文字テーブルを表す辞書
    
    Returns
    ----------
    midi_phrases : list(str)
        ポケットミクが扱う16進数文字列のリスト
    """
    
    midi_phrases = []
    for t in text.replace(' ', ''):
        midi_phrases.append(character_table[t])
    
    return midi_phrases

def make_voice(midi_output, notes, volumes, sleep_times):
    """
    ポケットミクに歌わせる関数．

    Parameters
    ----------
    midi_output : object
        pygamesのMIDI出力を扱うオブジェクト
    notes : list(int), range = [0, 127]
        音程，MIDIノート番号のリスト．真ん中のド(C4)の番号は60．
    volumes : list(int), range = [0, 255]
        音量のリスト．80くらいが良い感じ．
    sleep_times : list(float)
        音を発声する時間(s)
    """

    for n, v, s in zip(notes, volumes, sleep_times):
        midi_output.note_on(n, v)
        time.sleep(s)

    midi_output.note_off(notes[-1], volumes[-1])  # 止める

def main():
    midi_output = midi_setup(INSTURUMENT)

    # 歌詞
    ctable = get_character_table()
    text = 'なつがすぎ かぜあざみ だれのあこがれに さまよう' + \
           'あおぞらに のこされた わたしのこころは なつもよう'
    lyrics = get_midi_phrases(text, ctable)
    data = EXCLUSIVE_FIRST + lyrics + EXCLUSIVE_LAST
    
    # 音の情報
    notes_pattern_1 = [64, 64, 64, 62, 67, 64, 65, 64, 62, 60]
    notes_pattern_2 = [57, 59, 60, 60, 55, 55, 60, 60, 60, 59, 60, 62]
    notes_pattern_3 = [57, 59, 60, 62, 64, 62, 60, 55, 57, 62, 59, 59, 60]
    notes = notes_pattern_1 + notes_pattern_2 + notes_pattern_1 + notes_pattern_3

    volumes = [80] * len(lyrics)
    
    sleep_pattern_1 = [0.8, 0.4, 0.4, 0.8, 0.8, 0.4, 0.4, 0.4, 0.2, 1.25]
    sleep_pattern_2 = [0.6, 0.4, 0.2, 0.4, 0.4, 0.4, 0.4, 0.6, 0.4, 0.4, 0.4, 1.2]
    sleep_pattern_3 = [0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.8]
    sleep_times = sleep_pattern_1 + sleep_pattern_2 + sleep_pattern_1 + sleep_pattern_3
    print(len(notes), len(volumes), len(sleep_times))

    # setting lyric by sending SysEx
    midi_output.write_sys_ex(pygame.midi.time(), data)

    make_voice(midi_output, notes, volumes, sleep_times)

    # リリース
    del midi_output
    pygame.midi.quit()

if __name__ == "__main__":
    main()