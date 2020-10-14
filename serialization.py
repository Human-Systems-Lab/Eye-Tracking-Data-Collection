from abc import ABC, abstractmethod
from typing import Tuple

import boto3


class Serializer(ABC):
    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            print(f'exc_type: {exc_type}')
            print(f'exc_value: {exc_val}')
            print(f'exc_traceback: {exc_tb}')

    @abstractmethod
    def handle_data(self, point: Tuple[float, float], frame) -> None:
        """
        Serializes a frame of data to the selected location

        :param point: the location on the screen where the person was prompted to look
        :param frame: picture of person looking at point
        """


class DiskSerializer(Serializer):
    def __init__(self, path):
        pass

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

    def handle_data(self, point: Tuple[float, float], frame) -> None:
        raise NotImplementedError()


class S3Serializer(Serializer):
    def __init__(self, bucket, aws_access_key_id=None, aws_secret_access_key=None):
        self.client = boto3.client(
            service_name="s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bucket = bucket

    def __enter__(self):
        raise NotImplementedError()

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)

    def handle_data(self, point: Tuple[float, float], frame) -> None:
        raise NotImplementedError()
