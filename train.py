import numpy as np
import torch
import time
import copy
import tqdm.notebook as tqdm
from config import DEVICE

def train_model(model, criterion, optimizer, scheduler, dataloaders, data_sizes, num_epochs=10):
    """
    Trains a model and logs training/validation loss, accuracy, and learning rate.

    Args:
        model: The PyTorch model to train.
        criterion: Loss function.
        optimizer: Optimizer for training.
        scheduler: Learning rate scheduler.
        dataloaders (dict): Dictionary containing 'train' and 'val' DataLoaders.
        data_sizes (dict): Dictionary containing sizes of 'train' and 'val' datasets.
        num_epochs (int): Number of epochs to train.

    Returns:
        model: The trained model with the best weights loaded.
    """
    since = time.time()
    best_model_wts = copy.deepcopy(model.state_dict())
    best_loss = np.inf

    for epoch in range(num_epochs):
        print(f'Epoch {epoch+1}/{num_epochs}\n')
        
        for phase in ['train', 'val']:
            if phase == 'train':
                model.train()
            else:
                model.eval()

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

                    if phase == 'train':
                        loss.backward()
                        optimizer.step()

                current_loss += loss.item() * inputs.size(0)
                current_corrects += torch.sum(preds == labels.data)

            epoch_loss = current_loss / data_sizes[phase]
            epoch_acc = current_corrects.double() / data_sizes[phase]

            print(f'{phase} Loss: {epoch_loss:.4f} | {phase} Accuracy: {epoch_acc:.4f}')

            # Log learning rate during training phase
            if phase == 'train':
                current_lr = scheduler.get_last_lr()[0]  # Get the current learning rate
                print(f"Learning Rate: {current_lr:.6f}")

            # Update scheduler based on validation loss
            if phase == 'val':
                scheduler.step(epoch_loss)  # Adjust learning rate based on validation loss

                if epoch_loss < best_loss:
                    print(f'Validation loss decreased from {best_loss:.4f} to {epoch_loss:.4f}. Saving model...')
                    best_loss = epoch_loss
                    best_model_wts = copy.deepcopy(model.state_dict())

        print('\n')

    time_elapsed = time.time() - since
    print(f'Training complete in {time_elapsed // 60:.0f}m {time_elapsed % 60:.0f}s')
    print(f'Best val loss: {best_loss:.4f}')

    # Load best model weights
    model.load_state_dict(best_model_wts)
    return model
