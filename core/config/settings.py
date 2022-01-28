import dataclasses 
from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class KafkaConsumerConfig:
    topic: Union[List[str], str] = field(default="testing")
    bootstrap_servers: str = field(default="localhost:9092")
    enable_auto_commit: bool = field(default=True)
    auto_offset_reset: str = field(default='earliest')

    @property
    def asdict(self):
        _cls_dict = dataclasses.asdict(self)
        _cls_dict.pop('topic')
        return _cls_dict
        
@dataclass
class KafkaProducerConfig:
    topic: List[str] = field(default="testing")
    bootstrap_servers: str = field(default="localhost:9092")
    max_request_size: int = field(default=1295725856)

    @property
    def asdict(self):
        _cls_dict = dataclasses.asdict(self)
        _cls_dict.pop('topic')
        return _cls_dict

@dataclass
class MinioConfig:
    endpoint: str = field(default="localhost:9000")
    access_key: str = field(default="testkey")
    secret_key: str = field(default="testsecret")

    @property
    def asdict(self):
        return dataclasses.asdict(self)
