import torch
from pytorch_lightning import LightningModule
from torch.utils.Dataset import Dataset, DataLoader
from core.clients import MinioHandler
from .augmentation import Augmentation
from typing import Dict, TypeVar

_Augmentation = TypeVar('_Augmentation')

class ClientDataset(Dataset):

    def __init__(self,
                 client: MinioHandler,
                 bucket_name: str,
                 transform: _Augmentation,
                 **kwargs):
        self.client = client
        self.bucket_name = bucket_name
        self.transform = transform
        self.images = self.client.list_objects(self.bucket_name, **kwargs)
    
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        image = self.client.get_object_from_bucket(self.bucket_name,
                                                   self.images[idx]._object_name)
        label = torch.tensor([int(self.images[idx]._object_name.split("_")[1])])
        if self.transform:
            image = self.transform(image)
        return image, label

class ClientDataModule(LightningModule):

    def __init__(self,
                 client: MinioHandler,
                 buckets: Dict[str, str]):
        self.client = client
        self.buckets = buckets
    
    def _create_dataloader(self, mode: str):
        if mode == 'train':
            return ClientDataset(self.client, bucket_name=self.buckets['train_bucket_name'], transform=Augmentation('train'))
        return ClientDataset(self.client, bucket_name=self.buckets['val_bucket_name'], transform=Augmentation('val'))
    
    def train_dataloader(self):
        dataset = self._create_dataloader('train')
        return DataLoader(dataset, batch_size=6, shuffle=True)
    
    def val_dataloader(self):
        dataset = self._create_dataloader('val')
        return DataLoader(dataset, batch_size=6, shuffle=True)
