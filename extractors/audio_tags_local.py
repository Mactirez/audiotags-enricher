import os
import json
import logging

from pathlib import Path
from datetime import datetime, timezone

from mutagen import File as MutagenFile
from mutagen.easyid3 import key
from mutagen.mp3 import MP3 as MutagenMP3
from mutagen.flac import FLAC as MutagenFLAC
from mutagen.id3 import USLT, SYLT
from dotenv import load_dotenv

from system.logging import setup_logging

logger = logging.getLogger('audio_tags_local.py')

AUDIO_EXTENSIONS = {".mp3", ".flac"}

load_dotenv()


def get_audio_track_and_disc_number(audio) -> tuple[Any | None, Any | None, Any | None, Any | None]:
    """Функция извлекает информацию о количестве песен и дисков и возвращает в упорядоченном виде."""

    track_number, track_total = None, None
    disc_number, disc_total = None, None

    track_row = audio.get("tracknumber")
    disc_row = audio.get("discnumber")

    if track_row:
        track_number, sep, track_total = track_row[0].partition("/")

    if disc_row:
        disc_number, sep, disc_total = disc_row[0].partition("/")

    return (track_number, track_total or None,
            disc_number, disc_total or None)


def get_audio_lyrics(audio_path: Path):
    """Функция извлекает текст песни если он присутствует."""

    lyrics = None
    language = None

    if audio_path.suffix.lower().endswith(".mp3"):

        audio = MutagenMP3(audio_path)

        for tag in audio.tags.values():
            if isinstance(tag, USLT):
                lyrics = tag.text
                language = tag.lang
                break

            elif isinstance(tag, SYLT):
                lyrics = tag.text
                language = tag.lang
                break

    elif audio_path.suffix.lower().endswith(".flac"):

        audio = MutagenFLAC(audio_path)

        lyrics_values = audio.get("lyrics")
        language_values = audio.get("language")
        lyrics = lyrics_values[0] if lyrics_values else None
        language = language_values[0] if language_values else None

    return lyrics, language


def get_audio_tag_basic(file_paths: list[Path]) -> dict:
    """Функция извлекает и собирает набор метаданных в зависимости от формата аудио файла."""

    row_audio_metadata = {}

    for track in file_paths:
        try:
            audio = MutagenFile(track, easy=True)

            if audio is None:
                logger.warning("Не удалось определить формат аудиофайла: %s", track)
                continue

            logger.info("Обработка файла: %s", track.name)
            audio_info = getattr(audio, 'info', None)
            audio_stats = track.stat()
            track_number, track_total, disc_number, disc_total = get_audio_track_and_disc_number(audio)
            lyrics, language = get_audio_lyrics(track)

        except FileNotFoundError as error:
            logger.exception("Не удалось прочитать файл %s. Ошибка: %s", track, error)
            continue

        tags = {
            "metadata": {
                "title": audio.get("title", [None]),  # Название композиции.
                "artist": audio.get("artist", [None]),  # Исполнитель композиции. Может содержать одного или нескольких исполнителей.
                "album": audio.get("album", [None]),  # Название альбома.
                "album_artist": audio.get("album_artist", [None]),  # Основной исполнитель альбома. Может отличаться от исполнителя трека.
                "genre": audio.get('genre', [None]),  # Жанр или список жанров композиции.
                "date": audio.get('date', [None]),  # Год выпуска.
                "track_number": track_number,  # Порядковый номер трека внутри альбома.
                "track_total": track_total,  # Общее количество треков в альбоме.
                "disc_number": disc_number,  # Порядковый номер диска в многодисковом издании.
                "disc_total": disc_total,  # Общее количество дисков в издании.
                "lyrics": lyrics,  # Текст песни, встроенный в аудиофайл.
                "language": language,  # Язык текста песни, указанный во встроенных тегах.
            },

            "cover": {
                "present": None,  # Признак наличия встроенной обложки: True или False.
                "size_bytes": None,  # Размер встроенной обложки в байтах.
            },

            "stream_info": {
                "duration_seconds": getattr(audio_info, 'length', None),  # Продолжительность аудиозаписи в секундах.
                "bitrate": getattr(audio_info, "bitrate", None),  # Битрейт аудиопотока в битах в секунду.
                "sample_rate": getattr(audio_info, "sample_rate", None),  # Частота дискретизации аудио в герцах.
                "channels": getattr(audio_info, "channels", None),  # Количество аудиоканалов: 1 - mono, 2 - stereo.
                "bits_per_sample": getattr(audio_info, "bits_per_sample", None),  # Разрядность аудио, например 16 или 24 бита.
            },

            "file_info": {
                "ateid": None,  # Внутренний уникальный идентификатор аудиофайла в AudioTags Enricher.
                "path_local": str(track),  # Полный локальный путь к аудиофайлу.
                "file_name": track.name,  # Имя файла вместе с расширением.
                "extension": track.suffix.lower(),  # Расширение файла, например .mp3 или .flac.
                "data_load": datetime.now(timezone.utc).isoformat(),  # Дата и время, когда AudioTags Enricher прочитал и загрузил сведения о файле.
                "data_edit": datetime.fromtimestamp(audio_stats.st_mtime, tz=timezone.utc).isoformat(),  # Дата и время последнего изменения в файловой системе.
            },
        }

        row_audio_metadata[str(track)] = tags

    return row_audio_metadata


def main():
    """Временная функция для управления сбором данных."""
    setup_logging(logfile_name="audio_tags_local")
    audio_path = [Path(os.getenv("audiopath"))]

    logger.info("Старт сбора локальных метаданных.")
    logger.info("Всего обнаружено файлов: %s", len(audio_path))

    track = get_audio_tag_basic(audio_path)

    logger.info("Конец сбора локальных метаданных.")

    print(track)


if __name__ == "__main__":
    main()
