import os
from pathlib import Path
import shutil

Source_folder= 

File_types={
    "Image_Files": ['.jpg','.jpeg','.png','.gif','.bmp'],
    "Video_Files": ['.mp4','.mkv','.avi','.mov','.flv'],    
    "Audio_Files": ['.mp3','.wav','.aac','.flac','.ogg'],
    "Other_Files": [],
    "Executable_Files": ['.exe','.bat','.sh','.msi','.apk'],
    "TXT_Files": ['.txt'],
    "PDF_Files": ['.pdf'],
    "Word_Files": ['.docx','.doc'],
    "Excel_Files": ['.xlsx','.xls','.csv'],
}

def organize_files():
    for file in Source_folder.iterdir():
        if file.is_dir():
            continue
        ext=file.suffix.lower()
        moved=False
        
        for folders,extension in File_types.items():
            if ext in extension:
                folder_path=Source_folder/folders
                folder_path.mkdir(exist_ok=True)
                #moving the file into folder
                shutil.move(str(file),str(folder_path/file.name))
                moved=True
                break
        if not moved:
            other_folder=Source_folder/'Other_Files'
            other_folder.mkdir(exist_ok=True)
            shutil.move(str(file),str(other_folder/file.name))
            
if __name__=="__main__":
    organize_files()
    print("Files organized successfully!")
    
        
        
        
        
