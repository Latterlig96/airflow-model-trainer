from typing import Any, Dict
import pytorch_lightning as pl
import torch
from core.clients import MinioHandler
from pytorch_lightning import callbacks
from pytorch_lightning.loggers.mlflow import MLFlowLogger
from pytorch_lightning.callbacks.early_stopping import EarlyStopping
from pytorch_lightning.utilities.seed import seed_everything
from .data import ClientDataModule
from .model import Model
import logging

class Trainer:

    def __init__(self, context: Dict[str, Any]):
        self._on_init_start()
        self.context = context
    
    def _on_init_start(self):
        seed_everything(47)
        self.client = MinioHandler()
        self.model = Model()
        self.logger = MLFlowLogger()
        earlystopping = EarlyStopping(monitor="val_loss", verbose=True, patience=30)
        lr_monitor = callbacks.LearningRateMonitor()
        loss_checkpoint = callbacks.ModelCheckpoint(filename="best_loss", monitor="val_loss",
                                                    save_top_k=1, mode="max", save_last=False)
        self.callbacks = [earlystopping, lr_monitor, loss_checkpoint]
        device = 'cuda' if torch.cuda.is_available else 'cpu'
        if device == 'cuda':
             torch.backends.cudnn.benchmark = True
        torch.autograd.set_detect_anomaly(True)


    def train(self):
        module = ClientDataModule(client=self.client, buckets=self.context['buckets'])
        trainer = pl.Trainer(
            logger=self.logger,
            max_epochs=100,
            callbacks=self.callbacks,
            gpus=1,
            accumulate_grad_batches=1,
            progress_bar_refresh_rate=1,
            fast_dev_run=1,
            num_sanity_val_steps=0,
            resume_from_checkpoint=None)
        trainer.fit(self.model, datamodule=module)
        logging.info("Training went successfully, you cant view logs on MLFLOW UI")
        return True
