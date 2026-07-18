import os
import json
import logging

from pathlib import Path
from mutagen import File as MutagenFile
from mutagen.easyid3 import key
from mutagen.mp3 import MP3 as MutagenMP3
from mutagen.flac import FLAC as MutagenFLAC
from mutagen.id3 import USLT, SYLT
from dotenv import load_dotenv

from system.logging import setup_logging

logger = logging.getLogger('audio_tags_local.py')

AUDIO_EXTENSIONS = {".mp3", ".flac"}
STREAM_INFO_FIELDS = ("length", "bitrate", "sample_rate", "channels", "bits_per_sample", "codec", "codec_description")

load_dotenv()

def get_audio_tag_basic(file_paths: list[Path]) -> dict:
    """Функция извлекает и собирает набор метаданных в зависимости от формата аудио файла."""

    row_audio_metadata = {}

    for track in file_paths:
        try:
            audio = MutagenFile(track, easy=True)

        except FileNotFoundError as error:
            logger.exception("Не удалось прочитать файл %s. Ошибка: %s", track, error)
            continue

        tags = {
            "ateid": None,  # Внутренний уникальный идентификатор аудиофайла в системе AudioTags Enricher.

            "metadata": {
                "title": audio.get("title", [None]),  # Название композиции из встроенных тегов аудиофайла.
                "artist": audio.get("artist", [None]),  # Исполнитель композиции. Может содержать одного или нескольких исполнителей.
                "album": audio.get("album", [None]),  # Название альбома.
                "album_artist": audio.get("album_artist", [None]),  # Основной исполнитель альбома. Может отличаться от исполнителя отдельного трека.
                "genre": audio.get('genre', [None]),  # Жанр или список жанров композиции.
                "date": audio.get('date', [None]),  # Дата или год выпуска, записанные во встроенных тегах файла.
                "track_number": None,  # Порядковый номер трека внутри диска или альбома.
                "track_total": None,  # Общее количество треков на диске или в альбоме.
                "disc_number": None,  # Порядковый номер диска в многодисковом издании.
                "disc_total": None,  # Общее количество дисков в издании.
                "lyrics": None,  # Текст песни, встроенный в аудиофайл.
                "language": None,  # Язык композиции или текста песни, указанный во встроенных тегах.
            },

            "cover": {
                "present": None,  # Признак наличия встроенной обложки: True или False.
                "size_bytes": None,  # Размер встроенной обложки в байтах.
            },

            "stream_info": {
                "duration_seconds": audio.info.length if hasattr(audio, "info") else None,  # Продолжительность аудиозаписи в секундах.
                "bitrate": None,  # Битрейт аудиопотока в битах в секунду.
                "sample_rate": None,  # Частота дискретизации аудио в герцах, например 44100.
                "channels": None,  # Количество аудиоканалов: 1 — mono, 2 — stereo.
                "bits_per_sample": None,  # Разрядность аудио, например 16 или 24 бита. Чаще используется для FLAC.
                "codec": None,  # Кодек или формат аудиопотока, например MP3 или FLAC.
            },

            "file_info": {
                "path_local": None, # Полный локальный путь к аудиофайлу.
                "file_name": None,  # Имя файла вместе с расширением.
                "extension": None,  # Расширение файла, например .mp3 или .flac.
                "data_load": None,  # Дата и время, когда AudioTags Enricher прочитал и загрузил сведения о файле.
                "data_edit": None,  # Дата и время последнего изменения файла в файловой системе.
            },
        }

        row_audio_metadata[str(track)] = tags

    return row_audio_metadata

def main():
    """Временная функция для управления сбором данных."""
    audio_path = [Path(os.getenv("audiopath"))]
    track = get_audio_tag_basic(audio_path)
    print(track)

if __name__ == "__main__":
    main()