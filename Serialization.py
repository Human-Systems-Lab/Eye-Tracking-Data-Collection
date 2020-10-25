import os
import json
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Tuple

import boto3
import cv2


def get_fmt(fmt: str, d: datetime) -> str:
    """
    Populates a file naming format with the current time

    :param d: The time value to use to populate the format
    :param fmt: The user defined format to be populated
    :return: string representation of the populated format
    """
    Y = str(d.year)
    M = str(d.month)
    D = str(d.day)
    h = str(d.hour)
    m = str(d.minute)
    s = str(d.second) + str(d.microsecond)[:3]
    fmt = bytearray(fmt, "utf-8")
    for i in range(len(fmt)):
        if fmt[i] == ord('Y'):
            fmt[i] = ord(Y[0])
            Y = Y[1:]
        elif fmt[i] == ord('M'):
            fmt[i] = ord(M[0])
            M = M[1:]
        elif fmt[i] == ord('D'):
            fmt[i] = ord(D[0])
            D = D[1:]
        elif fmt[i] == ord('h'):
            fmt[i] = ord(h[0])
            h = h[1:]
        elif fmt[i] == ord('m'):
            fmt[i] = ord(m[0])
            m = m[1:]
        elif fmt[i] == ord('s'):
            fmt[i] = ord(s[0])
            s = s[1:]
    return fmt.decode("utf-8")


def mkdir_file(file: str) -> None:
    """
    Creates all directories to allow writing to file.  Existing directories are kept

    :param file: The file for which a path must exist
    """
    dir_tree = file.replace('\\', '/').split('/')[:-1]
    base = ""
    for e in dir_tree:
        base = os.path.join(base, e)
        if not os.path.exists(base):
            os.mkdir(base)


class Serializer(ABC):
    @abstractmethod
    def close(self) -> None:
        """
        Flushes any internal buffers, and closes any connections to servers
        """

    @abstractmethod
    def handle_data(self, point: Tuple[float, float], frame) -> None:
        """
        Serializes a frame of data to the selected location

        :param point: the location on the screen where the person was prompted to look
        :param frame: picture of person looking at point
        """


class DiskSerializer(Serializer):
    def __init__(self, base_dir: str, img_dir: str, img_fmt: str, lbl_dir: str, lbl_fmt: str):
        self.img_dir = os.path.join(base_dir, img_dir)
        self.lbl_dir = os.path.join(base_dir, lbl_dir)
        self.img_fmt = img_fmt
        self.lbl_fmt = lbl_fmt

    def close(self) -> None:
        pass

    def handle_data(self, point: Tuple[float, float], frame) -> None:
        d = datetime.today()
        img_filename = os.path.join(self.img_dir, get_fmt(self.img_fmt, d) + ".jpg")
        lbl_filename = os.path.join(self.lbl_dir, get_fmt(self.lbl_fmt, d) + ".json")

        mkdir_file(img_filename)
        mkdir_file(lbl_filename)

        cv2.imwrite(img_filename, frame)
        with open(lbl_filename, "w") as f:
            json.dump(
                {
                    "x": point[0],
                    "y": point[1]
                },
                f
            )


class S3Serializer(Serializer):
    def __init__(self, bucket, aws_access_key_id=None, aws_secret_access_key=None):
        self.client = boto3.client(
            service_name="s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        self.bucket = bucket

    def close(self) -> None:
        pass

    def handle_data(self, point: Tuple[float, float], frame) -> None:
        raise NotImplementedError()
