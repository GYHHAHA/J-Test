from music21 import corpus, stream, note, midi
from Encoder import Encoding_BACH_From_Score
import numpy as np
import math

class Decoding_BACH_To_Score(): #解码器
    
    def __init__(self, Encoder, new_short_code = []):
        
        self.new_short_code = new_short_code #存放第一次解码后的信息
        self.Encoder = Encoder #由于要用到前面编码器的内部信息，导入该实例（还是一个类）
        
    def decode_oneHot_to_short_code(self, new_song, new_result, continue_pro=0.5, change_pro=0.7):
        #该函数的功能是进行第一次解码
        #但是第一次解码的结果与第一次编码的结果是不一样的，后者是存储音差，前者是存储数组下标，需要第二次解码时再转换
        self.new_short_code = []
        old_pitches = [0]*3 #音符指针初始化
        now_tick = 0 #时间指针初始化

        for tick_index in range(len(new_song)): #对时间节点循环
            tick = [now_tick, new_song[tick_index][1], new_song[tick_index][2]] #先加载给定声部信息
            for part in range(3): #对声部循环
                old_pitch = old_pitches[part] #记录上一次的音高
                new_pitch = np.argmax(new_result[tick_index, part, :len(new_result[0][0])-1]) #返回下标
                #此处的想法是，如果换音的概率不是太大，那么就不要换
                whether_changenote = new_result[tick_index, part, -1] > change_pro
                #这里与上面想法类似，如果概率最大的音的概率并不高，那么就保留前面那个音，这里用到了前一个音的音高信息
                if new_result[tick_index, part, old_pitch] > continue_pro:
                    pitch = old_pitch
                elif not whether_changenote: #决定是不是changenote
                    pitch = old_pitch
                else: pitch = new_pitch #若上述判断都通过，那么此时就应当改变音的状态了
                tick.append(pitch) #加入“音高”信息（其实为下标，不是真的音高）
                tick.append(int(whether_changenote)) #加入连续信息
                old_pitches[part] = pitch #保留此轮信息进入下一轮
            self.new_short_code.append(tick)
            now_tick += self.Encoder.min_tick #时间指针前进一个单位
    
    def change_tick(self, L, index):
        #这个函数是用来处理get_score中的tick操作，目的是将给定声部的两个值调换至正确的位置
        L_temp = L[1:3].copy() #copy则不会复制变量地址
        L.pop(1)
        L.pop(1) #因为前面index为1的已经不见了，所以还是去除现在index为1的
        L.insert(index *2 + 1, L_temp[0]) #将给定声部信息插入到正确位置，以备第二次解码
        L.insert(index *2 + 2, L_temp[1])

        return L
    
    def get_score(self):
        #该函数的功能是进行第二次解码，并输出到乐谱Score类型中
        new_score = stream.Score() #建立空乐谱
        #准备音符指针与声部初始化
        new_notes = [] 
        for part in range(4):
            new_score.insert(0, stream.Part())
            new_notes.append('ready?')
        for tick in self.new_short_code:
            #调用函数交换至正确顺序，思考若不调换会有什么后果
            tick = self.change_tick(tick, self.Encoder.appointed_voice_part) 
            for part_index in range(4): #对所有声部循环
                part = new_score.parts[part_index] #加载声部信息
                #准备使用下标索引
                pitch_index = part_index *2 + 1
                changenote_index = part_index *2 + 2
                #若不换音，则延续上一个音
                if new_notes[part_index] != 'ready?' and tick[changenote_index] == 0:
                    new_notes[part_index].quarterLength += self.Encoder.min_tick
                #如果要换音了
                if tick[changenote_index] == 1:
                    if tick[pitch_index] > 0: #非休止
                        new_ready_note = note.Note() #创建新的音 
                        new_notes[part_index] = new_ready_note
                        new_ready_note.offset = tick[0] #offset为该音的位置，设置为当前时间指针
                        if part_index == self.Encoder.appointed_voice_part:
                            #直接索引到tick该音的midi音高
                            new_ready_note.pitch.midi = tick[pitch_index]
                        else:
                            #此处的逻辑可能要草稿纸上画一画，需要完全弄清楚第一、第二次编码和第一次解码的输入输出才可以
                            new_ready_note.pitch.midi = tick[self.Encoder.appointed_voice_part *2 + 1] \
                            + tick[pitch_index] + self.Encoder.target_min
                        new_ready_note.quarterLength = self.Encoder.min_tick #调用最小时间单位设置长度
                        part.append(new_ready_note)
                    else:
                        new_ready_note = note.Rest() #建立休止符
                        new_notes[part_index] = new_ready_note #更新音符指针信息
                        new_ready_note.offset = tick[0]
                        new_ready_note.quarterLength = self.Encoder.min_tick
                        part.append(new_ready_note) #休止符加入声部信息
        
        return new_score #返回Score类型乐谱
    