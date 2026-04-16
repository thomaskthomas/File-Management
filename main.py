from pathlib import Path
import shutil


class FileOrganizer:

    FILE_TYPES = {
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
        self.organized_folders = set(self.FILE_TYPES.keys())
        self._validate_source()

    def _validate_source(self):
        if not self.source_folder.exists():
            raise FileNotFoundError(f"Source folder not found: {self.source_folder}")
        if not self.source_folder.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.source_folder}")

    def _get_target_folder(self, extension: str) -> str:
        for folder, extensions in self.FILE_TYPES.items():
            if extension in extensions:
                return folder
        return "Other_Files"

    def _move_file(self, file: Path, target_folder_name: str):
        target_folder = self.source_folder / target_folder_name
        target_folder.mkdir(exist_ok=True)
        shutil.move(str(file), str(target_folder / file.name))

    def _should_skip(self, file: Path) -> bool:
        return file.is_dir()

    def organize(self):
        moved, skipped = 0, 0

        for file in self.source_folder.iterdir():
            if self._should_skip(file):
                skipped += 1
                continue

            ext = file.suffix.lower()
            target = self._get_target_folder(ext)
            self._move_file(file, target)
            moved += 1

        print(f"Done — {moved} file(s) moved, {skipped} folder(s) skipped.")


if __name__ == "__main__":
    organizer = FileOrganizer("C:/Users/YourName/Downloads")
    organizer.organize()