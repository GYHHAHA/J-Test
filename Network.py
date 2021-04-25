import torch
from torch import nn
from torch.autograd import Variable
import tensorflow as tf

class BACH_Net(nn.Module):
    
    #网络的基本结构较简单，3个有300个隐藏层的LSTM，然后加两个线性层，最后是一个激活层和归一化层
    #LSTM非双向，双向做下来效果和单向差不多，但时间增加了，不划算
    #损失函数是带有mask的交叉熵函数
    
    def __init__(self, input_size, hidden_size, output_size, num_layers, max_length, lengths=[]):
        super(BACH_Net,self).__init__()
        self.lstm_layer = nn.LSTM(input_size,hidden_size,num_layers) #这里一定要搞清楚输入输出是什么，很重要
        self.Softmax = nn.Softmax(dim=3) #在Pytorch的0.4.0版本及其之后的版本，Softmax必须指定维度
        self.Sigmoid = nn.Sigmoid() #Sigmoid层
        self.Linearmiddle = nn.Linear(hidden_size,hidden_size) #第一个线性层
        self.Linearnote = nn.Linear(hidden_size,3*(output_size-1)) #第二个线性层中的音符层
        self.Linearchangenote = nn.Linear(hidden_size,3*1) #第二个线性层中的换音层
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.lengths = lengths #长度为5个，与batch数一致
        self.max_length = max_length #是batch最大长度，不是序列padding后的，padding后长度都一样
        
    def forward(self,x):
        #下面其实就做了一件事，根据batch做动态rnn输入
        #tensorflow里面只要调用dynamic_rnn就可以，但Pytorch不行
        #注意Pytorch的pack_padded_sequence函数默认序列长度递减输入
        #################################################################################
        _, idx_sort = torch.sort(self.lengths, dim=0, descending=True)
        _, idx_unsort = torch.sort(idx_sort, dim=0)
        length = torch.tensor(list(self.lengths[idx_sort])) #降序排列
        x = x[:,:length[0]]
        x_zeros = torch.zeros(5,self.max_length-length[0],self.hidden_size) #padding的长度
        x = x.index_select(0, idx_sort)
        x_packed = nn.utils.rnn.pack_padded_sequence(x,length,batch_first=True)
        x_packed,_ = self.lstm_layer(x_packed) #pack后的序列再输入lstm网络
        x_padded = nn.utils.rnn.pad_packed_sequence(x_packed,batch_first=True)
        x = x_padded[0].index_select(0, idx_unsort) #还原顺序
        if self.max_length-length[0]!=0:
            if torch.cuda.is_available():
                x = torch.cat((x.cuda(),x_zeros.cuda()),1)
            else:
                x = torch.cat((x,x_zeros),1) #将原始序列与padding的0拼接起来
        #################################################################################
        x = torch.reshape(x, [-1,self.hidden_size]) #准备转入线性层
        x = self.Linearmiddle(x) #传入第一层线性层
        
        notes = self.Linearnote(x)
        #下面需要注意shape要匹配好
        notes = self.Softmax(torch.reshape(notes,[5,self.max_length,3,(self.output_size-1)]))
        changenote = self.Linearchangenote(x)
        #changenote最后是一维，和note不一样
        changenote = self.Sigmoid(torch.reshape(changenote,[5, self.max_length,3,1]))
        
        x = torch.cat((notes, changenote),3) #在最后一个维度进行拼接

        return x

class LossFunction(nn.Module):
    
    def __init__(self):
        super(LossFunction, self).__init__()

    def forward(self,p,t):
        
        #此处为交叉熵函数，定义很简单，但必须利用torch内置函数，才能自动求导反向传播
        #比如在tensorflow中有clip截断函数，但torch中只能自己用数学方法凑出来，如下是我想的一个办法
        c_e = t*torch.log(1e-10*(1-p>1e-10).float()+p.mul((p>1e-10).float()).mul((p<1.0).float())+\
                          1.0*(1-(p<1.0).float()).float())+ (1-t)*torch.log(1e-10*(1-(1-p)>1e-10).float()+\
        (1-p).mul(((1-p)>1e-10).float()).mul(((1-p)<1.0).float())+1.0*(1-((1-p)<1.0).float()).float())
        c_e = -torch.sum(torch.sum(c_e,3),2) #此步为止为交叉熵定义，但此处需要有mask作用，避免padding值也算入误差
        mask = torch.sign(torch.max(torch.max(torch.abs(t),3)[0],2)[0]) #此处维度需要看清楚，在哪一个维加
        c_e*= mask #套上mask
        c_e = torch.sum(c_e,1)
        c_e/= torch.sum(mask,1) #输出列表

        return torch.mean(c_e.float()) #输出实数
