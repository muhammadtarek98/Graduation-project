from model.alexnet import MRI_alex
import torch
import torch.nn.functional as F
from torch.autograd import Variable
from tqdm import tqdm
from sklearn import metrics
def run_model(model, loader, train=False, optimizer=None, abnormal_model_path=None):
    preds = []
    labels = []
    if train:
        model.train()
    else:
        if abnormal_model_path:
            abnormal_model = MRI_alex()
            state_dict = torch.load(abnormal_model_path)
            abnormal_model.load_state_dict(state_dict)
            abnormal_model.cuda()
            abnormal_model.eval()
        model.eval()

    total_loss = 0.0
    num_batches = 0

    for batch in tqdm(loader):
        vol_axial, vol_sagit, vol_coron, label, abnormal = batch
        if train:
            if abnormal_model_path and not abnormal:
                continue
            optimizer.zero_grad()
        if loader.dataset.use_gpu:
            vol_axial, vol_sagit, vol_coron = vol_axial.cuda(), vol_sagit.cuda(), vol_coron.cuda()
            label = label.cuda()
        vol_axial, vol_sagit, vol_coron = Variable(vol_axial), Variable(vol_sagit), Variable(vol_coron)
        label = Variable(label)

        logit = model.forward(vol_axial, vol_sagit, vol_coron)

        loss = loader.dataset.weighted_loss(logit, label)
        total_loss += loss.item()

        pred = torch.sigmoid(logit)

        pred_npy = pred.data.cpu().numpy()[0][0]

        if abnormal_model_path and not train:
            abnormal_logit = abnormal_model.forward(vol_axial, vol_sagit, vol_coron)
            abnormal_pred = torch.sigmoid(abnormal_logit)
            abnormal_pred_npy = abnormal_pred.data.cpu().numpy()[0][0]
            pred_npy = pred_npy * abnormal_pred_npy

        label_npy = label.data.cpu().numpy()[0][0]

        preds.append(pred_npy)
        labels.append(label_npy)

        if train:
            loss.backward()
            optimizer.step()
        num_batches += 1

    avg_loss = total_loss / num_batches

    fpr, tpr, threshold = metrics.roc_curve(labels, preds)
    auc = metrics.auc(fpr, tpr)

    if abnormal_model_path and not train:
        del abnormal_model

    return avg_loss, auc, preds, labels
