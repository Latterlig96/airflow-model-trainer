from core.models.train import Trainer

trainer = Trainer(context={
    'buckets': {
        'train_bucket_name': 'sample-data-train',
        'val_bucket_name': 'sample-data-val'
    }
})

trainer.train()