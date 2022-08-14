# -*- coding: utf-8 -*-
import os
import csv
import torch

import numpy as np
import pandas as pd

import torch.nn.functional as F
from torch.utils.data import DataLoader

from sklearn.metrics import r2_score
from sklearn.model_selection import KFold

from tqdm import tqdm
import matplotlib.pyplot as plt

os.environ['CUDA_LAUNCH_BLOCKING'] = "1"

main_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(main_dir)

def read_file(filename, new_features=False, use_devs=True):
    data = pd.read_csv(filename)

    if new_features:
        X = data[[
            "qtd_commits_arquivo_variabilidade",
            "dl_variabilidade",
            "ac_variabilidade",
            "qtd_arquivos_variabilidade"
        ]]
    else:
        X = data[[
            "qtd_commits_arquivo_variabilidade",
            "dl_variabilidade",
            "ac_variabilidade",
            "qtd_arquivos_variabilidade",
            "fa_variabilidade"
        ]]

    X = X.iloc[:].values
    X = np.nan_to_num(X)
    if use_devs:
        y = data.id_desenvolvedor
    else:
        y = data.id_reviewer

    X_torch = torch.tensor(X, dtype = torch.float)
    Y_torch = torch.tensor(y, dtype = torch.float).view(-1, 1)

    return X.shape[1], y, torch.utils.data.TensorDataset(X_torch, Y_torch)

'''
1: CREATE MODEL CLASS
'''
class RegressionModel(torch.nn.Module):
  def __init__(self, input_dim, output_dim):
    super(RegressionModel, self).__init__()
    self.linear = torch.nn.Linear(input_dim, output_dim)

  def forward(self, x):
    out = self.linear(x)
    return out


def data_split(dataset, lists):
  return [torch.utils.data.Subset(dataset, llist) for llist in lists]


def train_model(dl, model, opt, criterion, epochs, device):

    model.to(device)
    model.train()

    mean_loss = []
    for epoch in tqdm(range(epochs), desc="Treino"):

        total = 0
        running_loss = 0
        for inputs, labels in dl:
            # input = entrada
            # labels = Y
            inputs = inputs.to(device)
            labels = labels.to(device)

            y_predicted = model(inputs) # resultado da última camada

            loss = criterion(y_predicted, labels)

            opt.zero_grad() # zera os gradientes
            loss.backward() # backpropagation
            opt.step() # atualiza os pesos

            total += labels.size(0)
            running_loss += loss.item()

        train_loss = running_loss / total
        mean_loss.append(train_loss)

    return np.mean(mean_loss)


def evaluate_model(dl, model, criterion, device):
    model.to(device)
    model.eval()

    total = 0
    correct = 0
    running_loss = 0

    eval_r2 = 0
    eval_mae = 0
    eval_mse = 0
    eval_rmse = 0

    with torch.no_grad():
        for data in tqdm(dl, desc="Avaliação"):
            x, y = data[0].to(device), data[1].to(device)
            
            y_predicted = model(x)
            loss = criterion(y_predicted, y)

            correct += (y_predicted.int() == y).sum().item()
            total += y.size(0)

            running_loss += loss.item()
        
            r2 = r2_score(y.cpu(), y_predicted.cpu())
            mae = F.l1_loss(y_predicted, y) # Mean Absolute Error
            mse = F.mse_loss(y_predicted, y) # Mean Squared error
            rmse = torch.sqrt(mse) # Root Mean Squared Error

            eval_r2 += r2
            eval_mae += mae.item()
            eval_mse += mse.item()
            eval_rmse += rmse.item()

    acc = 100 * correct / total
    test_loss = running_loss / total

    eval_r2 /= total
    eval_mae /= total
    eval_mse /= total
    eval_rmse /= total

    return test_loss, acc, eval_r2, eval_mae, eval_mse, eval_rmse


def test_model (p, batch_size, epochs, opt, learningRate, use_devs, new_features, input_file):
    device = torch.device('cuda:0')

    filename = os.path.join(main_dir, input_file)

    input_dim, y, dataset = read_file(filename, new_features, use_devs)
    output_dim = 1

    dl_test = torch.utils.data.DataLoader(dataset, batch_size = batch_size)

    model = RegressionModel(input_dim, output_dim)
    if new_features:
        model.load_state_dict(torch.load("novos_features_{}p_{}b_{}e_lr{}_{}.pth".format(p, batch_size, epochs, learningRate, opt)))
    else:
        model.load_state_dict(torch.load("latest_{}p_{}b_{}e_lr{}_{}.pth".format(p, batch_size, epochs, learningRate, opt)))

    # Print model's state_dict
    print("Model's state_dict:")
    for param_tensor in model.state_dict():
        print(param_tensor, "\t", model.state_dict()[param_tensor])

    model.to(device)
    model.eval()

    r2 = 0.0
    total = 0.0
    correct = 0.0
    with torch.no_grad():
        for x, y in dl_test:
            x = x.to(device)
            y = y.to(device)

            y_predicted = model(x)

            r2 += r2_score(y.cpu(), y_predicted.cpu())
            correct += (y_predicted.int() == y).sum().item()
            total += y.size(0)

    r2 /= total
    acc = 100 * correct / total

    print('Accuracy: {} \t r2: {}'.format(acc, r2))

    test_file = os.path.join(main_dir, "test_{}p.csv".format(p))

    write_header = False
    if not os.path.exists(test_file):
        write_header = True

    with open(test_file, "a") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames = ["nf", "epochs", "lr", "loss", "optim", "batch_size", "bias", "w0", "w1", "w2", "w3", "w4", "accuracy", "r2"])
        if write_header:
            writer.writeheader()

        weight = model.state_dict()['linear.weight'][0]

        writer.writerow({
            "nf": "novos_features" if new_features else "",
            "epochs": epochs,
            "lr": learningRate,
            "loss": "L1Loss",
            "optim": opt,
            "batch_size": batch_size,
            "bias": model.state_dict()['linear.bias'].item(),
            "w0": weight[0].item(),
            "w1": weight[1].item(),
            "w2": weight[2].item(),
            "w3": weight[3].item(),
            "w4": weight[4].item() if new_features else 0,
            "accuracy": acc,
            "r2": r2
        })


def run (p=43, batch_size=1024, epochs=1000, opt="SGD", learningRate=0.00001, momentum=0.9, n_splits=10, new_features=False, input_file=""):
    device = torch.device('cuda:0')

    best = -1000

    skf = KFold(n_splits = n_splits)
    filename = os.path.join(main_dir, input_file)

    input_dim, y, dataset = read_file(filename, new_features, False)
    output_dim = 1

    for i, (train, test) in enumerate(skf.split(dataset, y)):
        ds_train, ds_test = data_split(dataset, (train, test))

        print("Treinamento %d de %d" % (i + 1, n_splits))

        model = RegressionModel(input_dim, output_dim)

        dl_train = torch.utils.data.DataLoader(ds_train, batch_size = batch_size)
        dl_test  = torch.utils.data.DataLoader(ds_test, batch_size = batch_size)

        #criterion = torch.nn.NLLLoss()
        #criterion = torch.nn.CrossEntropyLoss()

        criterion = torch.nn.L1Loss()
        #criterion = torch.nn.MSELoss()
        #criterion = torch.nn.SmoothL1Loss()

        if opt == "Adam":
            optimizer = torch.optim.Adam(model.parameters(), lr=learningRate)
        elif opt == "SGD":
            optimizer = torch.optim.SGD(model.parameters(), lr=learningRate)
        else:
            optimizer = torch.optim.SGD(model.parameters(), lr=learningRate, momentum=momentum)

        train_loss = train_model(dl_train, model, optimizer, criterion, epochs, device)
        eval_loss, eval_acc, eval_r2, eval_mae, eval_mse, eval_rmse = evaluate_model(dl_test, model, criterion, device)

        print()
        print('Train Loss: {} \t Valid Loss: {}'.format(train_loss, eval_loss))
        print('Accuracy: {} \t r2: {}'.format(eval_acc, eval_r2))

        print("="*100)

        train_file = os.path.join(main_dir, "train_{}p.csv".format(p))

        write_header = False
        if not os.path.exists(train_file):
            write_header = True

        with open(train_file, "a") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames = ["fold", "nf", "epochs", "lr", "loss", "optim", "batch_size", "train_loss", "eval_loss", "accuracy", "r2", "mae", "mse", "rmse"])
            if write_header:
                writer.writeheader()

            writer.writerow({
                "fold": i + 1,
                "nf": "novos_features" if new_features else "",
                "epochs": epochs,
                "lr": learningRate,
                "loss": "L1Loss",
                "optim": opt,
                "batch_size": batch_size,
                "train_loss": train_loss,
                "eval_loss": eval_loss,
                "accuracy": eval_acc,
                "r2": eval_r2,
                "mae": eval_mae,
                "mse": eval_mse,
                "rmse": eval_rmse
            })

        if eval_acc > best:
            best = eval_acc
            if new_features:
                torch.save(model.state_dict(keep_vars = True), "novos_features_{}p_{}b_{}e_lr{}_{}.pth".format(p, batch_size, epochs, learningRate, opt))
            else:
                torch.save(model.state_dict(keep_vars = True), "latest_{}p_{}b_{}e_lr{}_{}.pth".format(p, batch_size, epochs, learningRate, opt))

    #test_model(p, batch_size, epochs, learningRate, opt)


projetos = 20
batch_size = 1024
epochs = 1000
opt = "SGD"
learningRates = [0.00001, 0.0001, 0.001]
momentum = 0.9
n_splits = 10
new_features = False
input_file = "n20_reviewers.csv"

for lr in learningRates:
    print(projetos, batch_size, epochs, opt, lr, momentum, n_splits)
    run (projetos, batch_size, epochs, opt, lr, momentum, n_splits, new_features, input_file)
    print("="*100)

    test_model(projetos, batch_size, epochs, opt, lr, False, new_features, "w17_reviewers.csv")
    test_model(projetos, batch_size, epochs, opt, lr, True, new_features, "w17_reviewers.csv")

