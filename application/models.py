import torch
import torch.nn as nn
from torchvision import models
import numpy as np
from torch.autograd import Variable
import os

class Model:
    def __init__(self, key = 'abnormal'):
        self.INPUT_DIM = 224
        self.MAX_PIXEL_VAL = 255
        self.MEAN = 58.09
        self.STDDEV = 49.73
        self.model_ab=MRI_alex(False)
        
        if key == 'abnormal':
            self.model_ab.load_state_dict(torch.load(r"models/abnormal.pt", map_location='cpu'))
        elif key =='acl':
            self.model_ab.load_state_dict(torch.load(r"models/acl.pt", map_location='cpu'))
        else:
            self.model_ab.load_state_dict(torch.load(r"models/men.pt", map_location='cpu'))
        self.model_ab.cuda()
    
    def preprocess(self, series):
        pad = int((series.shape[2] - self.INPUT_DIM)/2)
        series = series[:,pad:-pad,pad:-pad]
        series = (series-np.min(series))/(np.max(series)-np.min(series))*self.MAX_PIXEL_VAL
        series = (series - self.MEAN) / self.STDDEV
        series = np.stack((series,)*3, axis=1)
        series_float = torch.FloatTensor(series)
        return series_float
    
    def study(self, axial_path, sagit_path, coron_path):
        vol_axial = np.load(axial_path)
        vol_sagit = np.load(sagit_path)
        vol_coron = np.load(coron_path)
        vol_axial_tensor = self.preprocess(vol_axial)
        vol_sagit_tensor = self.preprocess(vol_sagit)
        vol_coron_tensor = self.preprocess(vol_coron)    
        return {"axial": vol_axial_tensor,
                "sagit": vol_sagit_tensor,
                "coron": vol_coron_tensor}
    
    def predict(self, model, tensors, abnormality_prior=None):
        vol_axial = tensors["axial"].cuda()
        vol_sagit = tensors["sagit"].cuda()
        vol_coron = tensors["coron"].cuda()
        vol_axial = Variable(vol_axial)
        vol_sagit = Variable(vol_sagit)
        vol_coron = Variable(vol_coron)
        logit = model.forward(vol_axial, vol_sagit, vol_coron)
        pred = torch.sigmoid(logit)
        pred_npy = pred.data.cpu().numpy()[0][0]
    
        if abnormality_prior:
            pred_npy = pred_npy * abnormality_prior
        return pred_npy
    
    def get_prediction(self):
        self.predict(self.model_ab, self.study(axial_path, coronal_path, sagittal_path))
    
    


class MRI_alex(nn.Module):
    def __init__(self, training=True):
        super().__init__()
        self.axial_net = models.alexnet(pretrained=training)
        self.sagit_net = models.alexnet(pretrained=training)
        self.coron_net = models.alexnet(pretrained=training)
        self.gap_axial = nn.AdaptiveAvgPool2d(1)
        self.gap_sagit = nn.AdaptiveAvgPool2d(1)
        self.gap_coron = nn.AdaptiveAvgPool2d(1)
        self.classifier = nn.Linear(3*256, 1)
        return
    
    def forward(self,vol_axial, vol_sagit, vol_coron):
        vol_axial = torch.squeeze(vol_axial, dim=0)
        vol_sagit = torch.squeeze(vol_sagit, dim=0)
        vol_coron = torch.squeeze(vol_coron, dim=0)
        vol_axial = self.axial_net.features(vol_axial)
        vol_sagit = self.sagit_net.features(vol_sagit)
        vol_coron = self.coron_net.features(vol_coron)
        vol_axial = self.gap_axial(vol_axial).view(vol_axial.size(0), -1)
        x = torch.max(vol_axial, 0, keepdim=True)[0]
        vol_sagit = self.gap_sagit(vol_sagit).view(vol_sagit.size(0), -1)
        y = torch.max(vol_sagit, 0, keepdim=True)[0]
        vol_coron = self.gap_coron(vol_coron).view(vol_coron.size(0), -1)
        z = torch.max(vol_coron, 0, keepdim=True)[0]
        w = torch.cat((x, y, z), 1)
        out = self.classifier(w)
        return out
