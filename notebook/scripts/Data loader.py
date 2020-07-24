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
import Dataset_creation
def load_data(task, use_gpu):
    train_dir = "/content/drive/My Drive/MRNet-v1.0/train"
    valid_dir = "/content/drive/My Drive/MRNet-v1.0/valid"
    
    train_dataset = Dataset(train_dir, task, use_gpu)
    valid_dataset = Dataset(valid_dir, task, use_gpu)

    train_loader = data.DataLoader(train_dataset, batch_size=1, num_workers=11, shuffle=True)
    valid_loader = data.DataLoader(valid_dataset, batch_size=1, num_workers=11, shuffle=False)

    return train_loader, valid_loader
