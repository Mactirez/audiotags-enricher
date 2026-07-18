import os
import json
from sys import prefix

import boto3


from pathlib import Path
from datetime import datetime
from mypy_boto3_s3 import S3Client


def get_required_env(variable: str) -> str:
    """Функция получает путь из переменной окружения и проверяет, что она задана."""

    value = os.getenv(variable)

    if value is None or value == "":
        raise ValueError(f"Не найдена обязательная переменная окружения: {variable}")

    return value

def create_s3_client() -> S3Client:
    """Функция создаёт клиент для подключения к S3-совместимому хранилищу."""

    return boto3.client(
        service_name="s3",
        endpoint_url=get_required_env("S3_ENDPOINT_URL"),
        aws_access_key_id=get_required_env("S3_ACCESS_KEY"),
        aws_secret_access_key=get_required_env("S3_SECRET_KEY"),
        region_name=get_required_env("S3_REGION")
    )

def upload_file(client: S3Client, filepath: Path, bucket: str, object_key: str) -> None:
    """Функция для загрузки одного файла в S3-совместимое хранилище."""

    if not filepath.is_file():
        raise FileNotFoundError(f"Не найден локальный файл для загрузки: {filepath}")

    created_at = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix_object_key = f"raw/local/{created_at}_{object_key}"

    client.upload_file(
        Filename=str(filepath),
        Bucket=bucket,
        Key=prefix_object_key
    )