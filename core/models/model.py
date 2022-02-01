import timm
import torch.nn as nn
import torch
from pytorch_lightning import LightningModule
import torchmetrics
from typing import Dict, Any


class EfficientNetB1(nn.Module):

    def __init__(self):
        super().__init__()
        self.backbone = timm.create_model(
            'efficientnet_b1', pretrained=True, num_classes=0, in_chans=3
        )
        num_features = self.backbone.num_features
        self.head = nn.Linear(num_features, 1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.backbone(x)
        out = self.head(out)
        return out

class Model(LightningModule):

    def __init__(self):
        super().__init__()
        self._build_model()
        self._build_criterion()
        self._build_metric()

    def _build_model(self):
        self.model = EfficientNetB1()
    
    def _build_criterion(self):
        self.criterion = torch.nn.BCEWithLogitsLoss()
    
    def _build_optimizer(self):
        self.optimizer = torch.optim.Adam(self.parameters(), lr=1e-5)
    
    def _build_scheduler(self): 
        self.scheduler = torch.optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer, T_0=20, eta_min=1e-4
        )
    
    def _build_metric(self):
        self.metric = torchmetrics.F1Score(num_classes=1)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out = self.model(x)
        return out
    
    def training_step(self, batch, batch_idx):
        loss, pred, labels = self._share_step(batch)
        return {'loss': loss, 'pred': pred, 'labels': labels}
    
    def validation_step(self, batch, batch_idx):
        loss, pred, labels = self._share_step(batch)
        return {'loss': loss.detach(), 'pred': pred.detach(), 'labels': labels.detach()}
    
    def training_epoch_end(self, outputs):
        self._share_epoch_end(outputs, 'train')
    
    def validation_epoch_end(self, outputs):
        self._share_epoch_end(outputs, 'val')
    
    def _share_step(self, batch):
        images, labels = batch
        pred = self.forward(images.float()).sigmoid()
        loss = self.criterion(pred, labels.float())
        return loss, pred, labels
    
    def _share_epoch_end(self, outputs, mode):
        preds = []
        labels = []
        for output in outputs:
            pred, label = output['pred'], output['labels']
            preds.append(pred)
            labels.append(label)
        preds = torch.cat(preds)
        labels = torch.cat(labels)
        metric = self.metric(preds, labels)
        self.log(f'{mode}_loss', metric)

    def configure_optimizers(self) -> Dict[Any, Any]:
        self._build_optimizer()
        self._build_scheduler()
        return {"optimizer": self.optimizer, "lr_scheduler": self.scheduler}
