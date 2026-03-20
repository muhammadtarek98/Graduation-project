import torch,datetime
from model.running import run_model

def train(rundir, task, epochs, learning_rate, use_gpu, model, abnormal_model_path=None):
    train_loader, valid_loader = load_data(task, use_gpu)
    model = model
    if use_gpu:
        model = model.cuda()
    optimizer = torch.optim.Adam(model.parameters(), learning_rate, weight_decay=0.01)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.3, threshold=1e-4)
    best_val_loss = float('inf')
    start_time = datetime.now()
    for epoch in range(epochs):
        change = datetime.now() - start_time
        print('starting epoch {}. time passed: {}  : lr = {} '.format(epoch + 1, str(change), learning_rate))

        train_loss, train_auc, _, _ = run_model(model, train_loader, train=True, optimizer=optimizer,
                                                abnormal_model_path=abnormal_model_path)

        print(f'train loss: {train_loss:0.4f}')
        print(f'train AUC: {train_auc:0.4f}')

        val_loss, val_auc, _, _ = run_model(model, valid_loader, abnormal_model_path=abnormal_model_path)

        print(f'valid loss: {val_loss:0.4f}')
        print(f'valid AUC: {val_auc:0.4f}')

        scheduler.step(val_loss)