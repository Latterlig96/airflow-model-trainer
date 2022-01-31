import albumentations as A
from albumentations.pytorch.transforms import ToTensorV2
import numpy as np
from typing import Union

class TrainAugmentation:

    def __init__(self):
        self.augmentation = A.Compose([A.Resize(height=256, width=256, p=1),
                                       A.HorizontalFlip(),
                                       A.VerticalFlip(),
                                       A.RandomBrightnessContrast(),
                                       ToTensorV2()], p=1)
    
    def __call__(self, x: np.ndarray):
        transform = self.augmentation(image=x)
        return transform['image']
    

class TestAugmentation:

    def __init__(self):
        self.augmentation = A.Compose([A.Resize(height=256, width=256, p=1),
                                       ToTensorV2()], p=1)
    
    def __call__(self, x: np.ndarray):
        transform = self.augmentation(image=x)
        return transform['image']

class Augmentation:

    def __init__(self, mode: str):
        self._get_augmentation_by_mode(mode)
    
    def _get_augmentation_by_mode(self,
                                 mode: str) -> Union[TrainAugmentation, TestAugmentation]:
        if mode == "val" or mode == "test":
            return TestAugmentation()
        return TrainAugmentation()
