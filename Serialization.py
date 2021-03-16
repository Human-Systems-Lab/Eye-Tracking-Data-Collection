import os
import io
import json
import platform
from datetime import datetime
from abc import ABC, abstractmethod
from typing import Tuple

import boto3
import cv2

plat = platform.system()
if plat == "Windows":
    cache_dir = os.path.join(os.getenv("APPDATA"), "HSL")
else:
    cache_dir = os.path.join(os.path.expanduser("~"), ".HSL")
cache_dir = os.path.join(cache_dir, "EyeTracking-DataCollection", "cache")


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
    print(fmt, Y, M, D, h, m, s)
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
    if platform.system() == "Linux":
        dir_tree = dir_tree[1:]
        dir_tree[0] = '/' + dir_tree[0]
    base = ""
    for e in dir_tree:
        base = os.path.join(base, e)
        if not os.path.exists(base):
            os.mkdir(base)


class Serializer(ABC):
    @abstractmethod
    def handle_data(self, point: Tuple[float, float], frame) -> None:
        """
        Serializes a frame of data to the selected location

        :param point: the location on the screen where the person was prompted to look
        :param frame: picture of person looking at point as a numpy array (cv2.*Capture)
        """


class DiskSerializer(Serializer):
    def __init__(
            self,
            base_dir: str,
            img_dir: str,
            img_fmt: str,
            lbl_dir: str,
            lbl_fmt: str
    ):
        self.img_dir = os.path.join(base_dir, img_dir)
        self.lbl_dir = os.path.join(base_dir, lbl_dir)
        self.img_fmt = img_fmt.replace("\\", '/')
        self.lbl_fmt = lbl_fmt.replace("\\", '/')

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
    def __init__(
            self,
            bucket: str,
            img_dir: str,
            img_fmt: str,
            lbl_dir: str,
            lbl_fmt: str,
            aws_access_key_id: str = None,
            aws_secret_access_key: str = None
    ):
        self.client = boto3.client(
            service_name="s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        self.bucket = bucket
        self.img_dir = img_dir.replace("\\", '/')
        self.img_fmt = img_fmt.replace("\\", '/')
        self.lbl_dir = lbl_dir.replace("\\", '/')
        self.lbl_fmt = lbl_fmt.replace("\\", '/')

    def handle_data(self, point: Tuple[float, float], frame) -> None:
        tmp_filename = os.path.join(cache_dir, "tmp.jpg")
        cv2.imwrite(tmp_filename, frame)

        d = datetime.today()
        img_filename = self.img_dir + '/' + get_fmt(self.img_fmt, d) + ".jpg"
        lbl_filename = self.lbl_dir + '/' + get_fmt(self.lbl_fmt, d) + ".json"

        with open(tmp_filename, "rb") as f:
            self.client.upload_fileobj(f, self.bucket, img_filename)
        with io.StringIO() as f:
            json.dump(
                {
                    "x": point[0],
                    "y": point[1]
                },
                f
            )
            self.client.upload_fileobj(f, self.bucket, lbl_filename)
