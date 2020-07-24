import pdb
import torch
import torch.nn as nn
from torchvision import models
import numpy as np
import os
import pickle
import torch
import torch.nn.functional as F
import torch.utils.data as data
import pdb
from torch.autograd import Variable
import argparse
import matplotlib.pyplot as plt
import os
import numpy as np
import torch
from tqdm import tqdm
import argparse
import json
import numpy as np
import os
import torch
from datetime import datetime
from pathlib import Path
from sklearn import metrics
import pdb
from sklearn import metrics
import argparse
import json
import numpy as np
import os
import torch
from datetime import datetime
from pathlib import Path
from sklearn import metrics
from torch.autograd import Variable

INPUT_DIM = 224
MAX_PIXEL_VAL = 255
MEAN = 58.09
STDDEV = 49.73

def preprocess(series):
        pad = int((series.shape[2] - INPUT_DIM)/2)
        series = series[:,pad:-pad,pad:-pad]
        series = (series-np.min(series))/(np.max(series)-np.min(series))*MAX_PIXEL_VAL
        series = (series - MEAN) / STDDEV
        series = np.stack((series,)*3, axis=1)
        series_float = torch.FloatTensor(series)
        return series_float

class Dataset(data.Dataset):
    def __init__(self, datadir, tear_type, use_gpu):
        super().__init__()
        self.use_gpu = use_gpu
        label_dict = {}
        self.paths = []
        abnormal_label_dict = {}
        if datadir[-1]=="/":
            datadir = datadir[:-1]
        self.datadir = datadir
        for i, line in enumerate(open(datadir+'-'+tear_type+'.csv').readlines()):
            line = line.strip().split(',')
            filename = line[0]
            label = line[1]
            label_dict[filename] = int(label)
        

        for i, line in enumerate(open(datadir+'-'+"abnormal"+'.csv').readlines()):
            line = line.strip().split(',')
            filename = line[0]
            label = line[1]
            abnormal_label_dict[filename] = int(label)

        for filename in os.listdir(os.path.join(datadir, "axial")):
            if filename.endswith(".npy"):
                self.paths.append(filename)
        
        self.labels = [label_dict[path.split(".")[0]] for path in self.paths]
        self.abnormal_labels = [abnormal_label_dict[path.split(".")[0]] for path in self.paths]

        if tear_type != "abnormal":
            temp_labels = [self.labels[i] for i in range(len(self.labels)) if self.abnormal_labels[i]==1]
            neg_weight = np.mean(temp_labels)
        else:
            neg_weight = np.mean(self.labels)
        
        self.weights = [neg_weight, 1 - neg_weight]

    def weighted_loss(self, prediction, target):
        weights_npy = np.array([self.weights[int(t[0])] for t in target.data])
        weights_tensor = torch.FloatTensor(weights_npy)
        if self.use_gpu:
            weights_tensor = weights_tensor.cuda()
        loss = F.binary_cross_entropy_with_logits(prediction, target, weight=Variable(weights_tensor))
        return loss

    def __getitem__(self, index):
        filename = self.paths[index]
        vol_axial = np.load(os.path.join(self.datadir, "axial", filename))
        vol_sagit = np.load(os.path.join(self.datadir, "sagittal", filename))
        vol_coron = np.load(os.path.join(self.datadir, "coronal", filename))

        # axial
        vol_axial_tensor = preprocess(vol_axial)
        
        # sagittal
        vol_sagit_tensor = preprocess(vol_sagit)

        # coronal
        vol_coron_tensor = preprocess(vol_coron)

        label_tensor = torch.FloatTensor([self.labels[index]])

        return vol_axial_tensor, vol_sagit_tensor, vol_coron_tensor, label_tensor, self.abnormal_labels[index]

    def __len__(self):
        return len(self.paths)
