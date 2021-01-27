import pickle
import numpy as np
import re
import time
from Bio.Seq import Seq
from ReadData import *

data_dir = "../data/prueba"
categories = ["OPN", "BUB8", "BUB10", "BUB12", "VRNORM"]
temperatures = ['308.0', '308.3', '308.6', '308.9', 
                '309.2', '309.5', '309.8', 
                '310', '310.1', '310.4', '310.7', 
                '311.0', '311.3', '311.6', '311.9',
                '312.2', '312.5', '312.8',
                '315', '320', '325', '330', '335', '340', '345', '350', '355', '360']

X_test_file = open('../data/serialized/X_test_channels_onehot_noAA.pkl', 'rb')
y_test_file = open('../data/serialized/y_test_channels_onehot_noAA.pkl', 'rb')
X_test = pickle.load(X_test_file)
y_test = pickle.load(y_test_file)
X_test_file.close()
y_test_file.close()

X_test_opn = X_test[:,1,:,0]
X_test_seq = X_test[:,1,:,5:9]

print(X_test_seq.shape)
print(X_test_opn.shape)