from pathlib import Path
import shutil

Source_folder = Path("C:/Users/YourName/Downloads")

File_types = {
    "Image_Files": ['.jpg','.jpeg','.png','.gif','.bmp'],
    "Video_Files": ['.mp4','.mkv','.avi','.mov','.flv'],    
    "Audio_Files": ['.mp3','.wav','.aac','.flac','.ogg'],
    "Executable_Files": ['.exe','.bat','.sh','.msi','.apk'],
    "TXT_Files": ['.txt'],
    "PDF_Files": ['.pdf'],
    "Word_Files": ['.docx','.doc'],
    "Excel_Files": ['.xlsx','.xls','.csv'],
}

ORGANIZED_FOLDERS = set(File_types.keys())

def organize_files():
    for file in Source_folder.iterdir():

        # Skip already organized folders
        if file.is_dir() and file.name in ORGANIZED_FOLDERS:
            continue

        # Skip any folder
        if file.is_dir():
            continue

        ext = file.suffix.lower()
        moved = False
        
        for folder, extensions in File_types.items():
            if ext in extensions:
                folder_path = Source_folder / folder
                folder_path.mkdir(exist_ok=True)

                shutil.move(str(file), str(folder_path / file.name))
                moved = True
                break

        if not moved:
            other_folder = Source_folder / 'Other_Files'
            other_folder.mkdir(exist_ok=True)
            shutil.move(str(file), str(other_folder / file.name))


if __name__ == "__main__":
    organize_files()
    print("Files organized successfully!")