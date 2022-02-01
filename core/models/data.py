import torch
from pytorch_lightning import LightningModule
from torch.utils.data import Dataset, DataLoader
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
        image = self.client.get_object_from_bucket(bucket_name=self.bucket_name,
                                                   object_name=self.images[idx]._object_name)
        label = torch.tensor([int(self.images[idx]._object_name.split("_")[1].replace('.jpg', ''))])
        if self.transform:
            image = self.transform(image)
        return image, label

class ClientDataModule(LightningModule):

    def __init__(self,
                 client: MinioHandler,
                 buckets: Dict[str, str]):
        super().__init__()
        self.client = client
        self.buckets = buckets
    
    def _create_dataloader(self, mode: str):
        if mode == 'train':
            return ClientDataset(self.client, bucket_name=self.buckets['train_bucket_name'], transform=Augmentation.get_augmentation_by_mode('train'))
        return ClientDataset(self.client, bucket_name=self.buckets['val_bucket_name'], transform=Augmentation.get_augmentation_by_mode('val'))
    
    def train_dataloader(self):
        dataset = self._create_dataloader('train')
        return DataLoader(dataset, batch_size=6, shuffle=True, num_workers=6)
    
    def val_dataloader(self):
        dataset = self._create_dataloader('val')
        return DataLoader(dataset, batch_size=6, num_workers=6)
