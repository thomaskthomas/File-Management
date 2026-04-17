from pathlib import Path
import shutil
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


class FileOrganizer:

    FILE_TYPES: dict[str, list[str]] = {
        "Image_Files":      ['.jpg', '.jpeg', '.png', '.gif', '.bmp'],
        "Video_Files":      ['.mp4', '.mkv', '.avi', '.mov', '.flv'],
        "Audio_Files":      ['.mp3', '.wav', '.aac', '.flac', '.ogg'],
        "Executable_Files": ['.exe', '.bat', '.sh', '.msi', '.apk'],
        "TXT_Files":        ['.txt'],
        "PDF_Files":        ['.pdf'],
        "Word_Files":       ['.docx', '.doc'],
        "Excel_Files":      ['.xlsx', '.xls', '.csv'],
    }

    def __init__(self, source: str):
        self.source_folder = Path(source)
        # Flatten to a reverse lookup: ext -> folder  (O(1) vs O(n) per file)
        self._ext_map: dict[str, str] = {
            ext: folder
            for folder, exts in self.FILE_TYPES.items()
            for ext in exts
        }
        self._validate_source()

    def _validate_source(self):
        if not self.source_folder.exists():
            raise FileNotFoundError(f"Source folder not found: {self.source_folder}")
        if not self.source_folder.is_dir():
            raise NotADirectoryError(f"Not a directory: {self.source_folder}")

    def _get_target_folder(self, extension: str) -> str:
        return self._ext_map.get(extension, "Other_Files")

    def _move_file(self, file: Path, target_folder_name: str) -> bool:
        target_folder = self.source_folder / target_folder_name
        target_folder.mkdir(exist_ok=True)
        destination = target_folder / file.name

        # Avoid overwriting duplicates — append a counter suffix
        counter = 1
        while destination.exists():
            destination = target_folder / f"{file.stem}_{counter}{file.suffix}"
            counter += 1

        shutil.move(str(file), str(destination))
        logger.debug("Moved: %s → %s", file.name, target_folder_name)
        return True

    def organize(self) -> dict[str, int]:
        stats = {"moved": 0, "skipped": 0, "failed": 0}

        for file in self.source_folder.iterdir():
            if file.is_dir():
                stats["skipped"] += 1
                continue

            try:
                target = self._get_target_folder(file.suffix.lower())
                self._move_file(file, target)
                stats["moved"] += 1
            except (OSError, shutil.Error) as e:
                logger.warning("Failed to move '%s': %s", file.name, e)
                stats["failed"] += 1

        logger.info(
            "Done — %d moved, %d skipped, %d failed.",
            stats["moved"], stats["skipped"], stats["failed"]
        )
        return stats


if __name__ == "__main__":
    organizer = FileOrganizer("C:/Users/YourName/Downloads")
    organizer.organize()