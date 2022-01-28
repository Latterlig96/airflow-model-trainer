import io
import logging
from typing import Any, Union, TypeVar
import cv2
import numpy as np
from minio import Minio
from minio.error import S3Error
from config import MinioConfig
from urllib3.exceptions import MaxRetryError
from airflow.models import Variable

_MinioClient = TypeVar('_MinioClient')

class MinioHandler:

    AIRFLOW_KEYS = ('endpoint', 'access_key', 'secret_key')

    def __init__(self):
        self._client = self._minio_hook()

    def _minio_hook(self) -> Union[_MinioClient, Exception]:
        result = self._get_variables()
        if result:
            config = MinioConfig(**self._variables)
            try:
                client = Minio(**config.asdict, secure=False)
                return client
            except (S3Error, MaxRetryError) as e:
                logging.exception(e)
                return None
        config = MinioConfig()
        try:
            client = Minio(**config.asdict, secure=False)
            return client
        except (S3Error, MaxRetryError) as e:
            logging.exception(e)
            return None

    def _get_variables(self) -> bool:
        try:
            self.variables = {key: Variable.get(key) for key in self.AIRFLOW_KEYS}
            return True
        except KeyError as e:
            return False

    def create_bucket(self,
                      bucket_name: str,
                      **kwargs) -> bool:
        if self.bucket_exists(bucket_name):
            logging.info(
                f"Bucket name {bucket_name} already exists, creating bucket operation skipped")
            return True
        if "_" in bucket_name:
            logging.info(
                "Replacing all '_' characters with '-' to avoid unappropriate bucket creation")
            bucket_name = bucket_name.replace("_", "-")
        self._client.make_bucket(bucket_name, **kwargs)
        return True

    def list_objects(self,
                     bucket_name: str,
                     **kwargs):
        objects = []
        for _object in self._client.list_objects(bucket_name, **kwargs):
            objects.append(_object)
        return objects

    def bucket_exists(self,
                      bucket_name: str) -> bool:
        return True if self._client.bucket_exists(bucket_name) else False

    def bucket_object_generator(self,
                                bucket_name: str,
                                **kwargs):
        for _object in self._client.list_objects(bucket_name, **kwargs):
            yield _object

    def put_object_to_bucket(self,
                             bucket_name: str,
                             object_data: Any,
                             object_name: str,
                             **kwargs) -> None:
        if isinstance(object_data, str):
            try:
                with open(object_data, 'rb') as f:
                    object_data = io.BytesIO(f.read())
            except FileNotFoundError as e:
                raise FileNotFoundError(e)
        try:
            if isinstance(object_data, io.BytesIO):
                pass
            else:
                object_data = io.BytesIO(object_data)
            self._client.put_object(bucket_name=bucket_name,
                                   object_name=object_name,
                                   data=object_data,
                                   length=object_data.getbuffer().nbytes, **kwargs)
        except (TypeError, AttributeError) as e:
            logging.exception(e)

    def get_object_from_bucket(self,
                               bucket_name: str,
                               object_name: str,
                               to_numpy: bool = True,
                               **kwargs) -> Union[bytes, np.ndarray]:
        try:
            response = self._client.get_object(bucket_name,
                                              object_name, **kwargs)
        except S3Error as e:
            logging.exception(e)

        if to_numpy:
            buf = np.frombuffer(response.read(), np.uint8)
            return cv2.imdecode(buf, cv2.IMREAD_COLOR)
        return response.read()

    def clear_bucket(self,
                     bucket_name: str,
                     remove_bucket: bool = False,
                     **kwargs) -> None:
        bucket_objects = self._client.list_objects(bucket_name, **kwargs)
        for _object in bucket_objects:
            self._client.remove_object(bucket_name, _object._object_name)
        logging.info(f"Objects from {bucket_name} removed")
        if remove_bucket:
            logging.info(f"Removing bucket {bucket_name}")
            self._client.remove_bucket(bucket_name)
        return True

    def __call__(self, **kwargs) -> Union[None, Any]:
        if hasattr(self, kwargs['method']['name']):
            method = getattr(self, kwargs['method']['name'])
            result = method(**kwargs['method']['kwargs'])
            return result
        logging.error(
            f"Could not find a given method {kwargs['method']}, exiting")
        return None
