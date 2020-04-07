from music21 import corpus, stream, note, midi
import numpy as np
import math

class Encoding_BACH_From_Score(): #编码器
    
    def __init__(self, appointed_voice_part = 0, min_tick = 0.25, key_mode = 'major'):
        
        self.appointed_voice_part = appointed_voice_part #给定的声部
        self.min_tick = min_tick #最小时间单位
        self.key_mode = key_mode #调性（大调或小调）
        self.song_list = [] #输入曲目总表
        self.data_max = -100 #指定声部的音高最大值
        self.data_min = 100 #指定声部的音高最小值
        self.target_max = -100 #其他声部的音差最大值
        self.target_min = 100 #其他声部的音差最小值
        self.trans_pitch = {'A- major':4, 'E- major':-3, 'B- major':2, 'F major':7, 'C major':0, \
                            'G major':5, 'D major':-2, 'A major':3, 'E major':-4, } #移调字典
        
    def get_appointed_part(self, song): #对指定声部编码
        
        appointed_part = [] #准备提取给定声部
        now_tick = 0 #初始时间指针
        for note in song.parts[self.appointed_voice_part].flat.notes: #对每个音符逐步编码并加入指定声部列表
            while note.offset > now_tick: #处理休止符
                appointed_part.append([now_tick, 0, 1]) #利用三个维度表示音的状态
                now_tick += self.min_tick
            note_duration_tick = int(note.duration.quarterLength / self.min_tick) #计算每个音持续多少最小时间单位
            note_pitch = note.pitches[0].midi #得到该音符的音高数（返回值为整数，在0-127之间）
            #考虑遍历计算得到data集合音域宽度
            if note_pitch != 0: #0值pitch在music21中为休止，没有音高
                if note_pitch > self.data_max:
                    self.data_max = note_pitch
                if note_pitch < self.data_min:
                    self.data_min = note_pitch
            for tick in range(note_duration_tick): #以最小时间为单位添加音符状态
                if tick == 0:
                    appointed_part.append([now_tick, note_pitch, 1]) #新音符的第三维状态为1
                else:
                    appointed_part.append([now_tick, note_pitch, 0]) #若持续则第三维状态为0
                now_tick += self.min_tick #时间指针前进
        
        return appointed_part #返回被提取声部列表
    
    def pitch_diff(self, base_pitch, new_pitch): #比较两个音相差的半音数
        
        if base_pitch*new_pitch == 0: #休止符不比较
            return 0
        else:
            return new_pitch-base_pitch  
    
    def get_other_parts(self, song): #获取所有编码后的谱面信息
        
        appointed_part = self.get_appointed_part(song) #获取指定声部列表
        uncoded_part = list(range(4))
        uncoded_part.remove(self.appointed_voice_part) #得到还未编码的声部
        
        for voice_index in uncoded_part: #对其他声部循环
            part_note = song.parts[voice_index].flat.notes #得到其他某一个声部中所有音的信息
            note_index = 0 #初始化音符指针
            for encoded_tick in appointed_part: #对指定声部循环,更新列表信息
                now_tick = encoded_tick[0] #获取当前时间指针
                now_note = part_note[note_index] #获取当前时间所对应的音
                if now_note.offset + now_note.duration.quarterLength <= now_tick: #时间指针达到或超过音符指针
                    note_index += 1 #音符指针前进
                now_note = part_note[note_index] #查看是否音符指针是否前进，若是，则立即更新
                part_note_pitch = now_note.pitches[0].midi #获取当前时间点的音高
                if now_note.offset == now_tick: #新音符的第2个状态为1
                    encoded_tick.extend([self.pitch_diff(encoded_tick[1], part_note_pitch), 1])
                elif now_note.offset < now_tick: #若持续则第2个状态为0
                    encoded_tick.extend([self.pitch_diff(encoded_tick[1], part_note_pitch), 0])
                else: #补充休止符
                    encoded_tick.extend([0, 1])
                #考虑遍历计算得到target集合音差宽度，休止符不算
                if encoded_tick[1]*part_note_pitch != 0:
                    if self.pitch_diff(encoded_tick[1], part_note_pitch) > self.target_max:
                        self.target_max = self.pitch_diff(encoded_tick[1], part_note_pitch)
                    if self.pitch_diff(encoded_tick[1], part_note_pitch) < self.target_min:
                        self.target_min = self.pitch_diff(encoded_tick[1], part_note_pitch)
                    
        return appointed_part #返回全套列表（虽然名称叫appointed_part）
    
    def get_all_chorales(self):
        
        for chorale in corpus.chorales.Iterator(returnType='filename'): #这是巴赫众赞歌材料包，详情见官网
            song = corpus.parse(chorale) #加载该首合唱的全部信息
            if len(song.parts) == 4 and song.analyze('key').mode == self.key_mode:
                old_tune = str(song.analyze('key'))
                #若为指定的声部数量和调性才执行
                song.transpose(self.trans_pitch[str(song.analyze('key'))], inPlace = True) #调性归一化
                get_temp = self.get_other_parts(song)
                if len(get_temp) <= 450: #若过长则删去（选450的原因用matplotlib画一下分布就知道了）
                    self.song_list.append(get_temp) #加入新的乐曲
                    print('%4d: %20s, %10s → %6s'%(len(self.song_list), chorale, \
                                                        old_tune, song.analyze('key')))
                    
        return self.song_list #返回所有曲目编码列表
    
    def get_dataset(self): #数据集再编码后准备输入网络
        
        song_tick_length,X,Y = [],[],[] #分别定义时间长度列表，训练集{X,Y}
        for song in self.song_list: song_tick_length.append(len(song)) #获取每首乐曲的时间总长
        max_song_tick_length = int(np.max(np.array(song_tick_length)))
        print('最大长度为：%d 曲目量为：%d'%(max_song_tick_length,len(self.song_list)))
        #准备第二次编码
        for song in self.song_list:
            x,y = [],[]
            for song_tick in song:
                #利用局部oneHot编码对输入集合进行再次编码
                oneHot = [0]*(self.data_max - self.data_min + 1) #data音域宽度
                if song_tick[1] != 0: oneHot[song_tick[1] - self.data_min] = 1 #oneHot编码
                oneHot.append(song_tick[2])
                x.append(oneHot) #加入是否连续的信息
                #利用局部oneHot编码对其他声部集合进行再次编码
                other_parts = [] #准备填充其他声部的编码信息
                for part in range(3):
                    part_index = 3 + part*2 #参见原先第一次编码方式即可知
                    oneHot = [0]*(self.target_max - self.target_min + 1) #target音差宽度
                    if song_tick[part_index] != 0: oneHot[song_tick[part_index] - self.target_min] = 1
                    oneHot.append(song_tick[part_index + 1])
                    other_parts.append(oneHot)
                y.append(other_parts)
            #准备padding操作
            padding_length = max_song_tick_length - len(x) #序列需要padding的长度
            for turn in range(padding_length):
                x.append([0]*(self.data_max - self.data_min + 2)) #data集合的填充
                y.append([[0]*(self.target_max - self.target_min + 2)]*3) #target集合的填充
            X.append(x)
            Y.append(y)
        #此处进行格式转换（因为上面一些玄学的原因导致第三层是list类型的表，有人知道怎么直接弄请告诉我）
        npX,npY = [],[]
        for i in range(len(self.song_list)):
            for j in range(max_song_tick_length):
                for k in range(self.data_max - self.data_min + 2): #其实为种类数+1的值，只是计算种类有一个加1
                    npX.append(X[i][j][k])
        for i in range(len(self.song_list)):
            for j in range(max_song_tick_length):
                for k in range(3): #注意此处还有一维
                    for m in range(self.target_max - self.target_min + 2):
                        npY.append(Y[i][j][k][m])
        #制作词典，准备返回数据集
        dataset = {'data': np.array(npX).reshape(len(self.song_list),\
                            max_song_tick_length,(self.data_max - self.data_min + 2)), \
                   'target': np.array(npY).reshape(len(self.song_list),\
                            max_song_tick_length,3,(self.target_max - self.target_min + 2)), \
                   'seq_length': np.array(song_tick_length)}
        
        return dataset
    
    def load_new_chorales(self, song): 
        
        song = corpus.parse(song) #加载音乐信息
        song.transpose(self.trans_pitch[str(song.analyze('key'))], inPlace = True) #移调
        get_temp = self.get_other_parts(song) #得到四声部第一次编码结果
        self.song_list.append(get_temp) #加入song_list的尾部
    
    def get_new_input_and_length(self):
        
        new_dataset = self.get_dataset() #此时song_list已经更新
        in_put = new_dataset['data'][-5:] #由于是加入song_list的尾部，又每批是5个，故取后五个值
        seq_length = new_dataset['seq_length'][-5:]
        
        return in_put,seq_length #返回批次的信息，最后一个是需要预测的音乐
