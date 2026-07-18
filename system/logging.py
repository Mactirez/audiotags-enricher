import logging
import sys
from pathlib import Path


def setup_logging(logfile_name: str) -> None:
    """
    Функция настраивает модуль логирования.

    Создаёт папку logs (если не существует) и настраивает вывод логов
    одновременно в файл и в консоль.
    """

    root = Path(__file__).resolve().parent.parent
    directory = root / "logs"
    logfile_path = directory / logfile_name
    directory.mkdir(parents=True, exist_ok=True)

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.FileHandler(logfile_path, encoding="utf-8"), logging.StreamHandler()],
        force=True
    )
