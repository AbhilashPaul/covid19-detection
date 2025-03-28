import numpy as np
import torch
import time
import copy
import tqdm.notebook as tqdm
from sklearn.metrics import cohen_kappa_score

from config import DEVICE

def train_model(model, criterion, optimizer, scheduler, dataloaders, data_sizes, num_epochs=10):
    since = time.time()

    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = np.inf

    for epoch in range(num_epochs):
        print('Epoch {}/{}/n'.format(epoch+1, num_epochs))

        for phase in ['train', 'val']:
            model.train() if phase == "train" else model.eval()

            current_loss = 0.0
            current_corrects = 0

            for inputs, labels in tqdm.tqdm(dataloaders[phase], desc=phase, leave=False):
                inputs = inputs.to(DEVICE)
                labels = labels.to(DEVICE)

                optimizer.zero_grad()

                with torch.set_grad_enabled(phase == 'train'):
                    outputs = model(inputs)
                    _, preds = torch.max(outputs, 1)
                    loss = criterion(outputs, labels)

                    # backward + optimize only if in training phase
                    if phase == 'train':
                        loss.backward()
                        optimizer.step()
                if phase == 'train':
                    scheduler.step()

                # We want variables to hold the loss statistics
                current_loss += loss.item() * inputs.size(0)
                current_corrects += torch.sum(preds == labels.data)

            epoch_loss = current_loss / data_sizes[phase]
            epoch_acc = current_corrects.double() / data_sizes[phase]
            if phase == 'val':
                print('{} Loss: {:.4f} | {} Accuracy: {:.4f}'.format(phase, epoch_loss, phase, epoch_acc))
            else:
                print('{} Loss: {:.4f} | {} Accuracy: {:.4f}'.format(phase, epoch_loss, phase, epoch_acc))

            # EARLY STOPPING
            if phase == 'val' and epoch_loss < best_loss:
                print('Val loss Decreased from {:.4f} to {:.4f} \n Saving Weights... '.format(best_loss, epoch_loss))
                best_loss = epoch_loss
                best_model_wts = copy.deepcopy(model.state_dict())

        print('\n')

    time_since = time.time() - since
    print('Training complete in {:.0f}m {:.0f}s'.format(time_since // 60, time_since % 60))
    print('Best val loss: {:.4f}'.format(best_loss))

    # Load the best model weights and return it
    model.load_state_dict(best_model_wts)
    return model
