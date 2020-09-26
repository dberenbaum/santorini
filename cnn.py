import math
import numpy as np
import torch
import torch.nn.functional as F


MODEL_PATH = "santorini.pt"


def get_samples(tree, n=10):
    samples = []
    for s in tree.sample(n):
        samples.append(s)
    return samples


def convert_state(state):
    i = int(len(state)/2)
    levels = np.array(list(state[:i]), dtype=int) / 4
    players = np.array(list(state[i:]), dtype=int)
    players[players > 1] = -1
    return levels, players


def parse_record(record):
    state = record["_id"]
    target = record["wins"] / record["tries"]
    tries = record["tries"]
    return state, target, tries


def states_to_torch(states):
    state_splits = [convert_state(state) for state in states]
    x_flat = torch.as_tensor(state_splits, dtype=torch.float)
    x_dim = int(math.sqrt(x_flat.shape[2]))
    x = torch.reshape(x_flat, [len(states), 2, x_dim, x_dim])
    return x


def samples_to_torch(samples):
    states, targets, tries = list(zip(*(parse_record(record) for record in samples)))
    x = states_to_torch(states)
    y_flat = torch.as_tensor(targets, dtype=torch.float)
    y = torch.reshape(y_flat, [len(samples), 1])
    w_flat = torch.as_tensor(tries, dtype=torch.float)
    w = torch.reshape(w_flat, [len(samples), 1])
    return x, y, w


class ValueNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = torch.nn.Conv2d(2, 64, 3, padding=1)
        self.dropout1 = torch.nn.Dropout()
        self.dense1 = torch.nn.Linear(64*5*5, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.dropout1(x)
        x = x.view(-1, 64*5*5)
        x = self.dense1(x)
        return x


def train_epoch(model, x, y, w, learning_rate=1e-4):
    model.train()
    criterion = torch.nn.BCEWithLogitsLoss(weight=w)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
    y_pred = model(x)
    loss = criterion(y_pred, y)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return y_pred, loss


def predict_proba(model, x):
    model.eval()
    with torch.no_grad():
        y_pred = model(x)
        return torch.sigmoid(y_pred)


def to_numpy(t):
    return t.squeeze().detach().numpy()


def max_state(states, model):
    x = states_to_torch(states)
    probs = predict_proba(model, x)
    idxmax = to_numpy(probs).argmax()
    return states[idxmax]


def load_model(model_path=MODEL_PATH):
    model = ValueNet()
    model.load_state_dict(torch.load(model_path))
    return model
