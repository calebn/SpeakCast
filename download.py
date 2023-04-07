import subprocess
import os
import requests
from urllib.parse import urlparse
from config import FRAME_RATE

def download_file(url, dest_folder):
    """
    Downloads a file from the given URL and saves it to the specified destination folder.
    
    Args:
        url (str): The URL of the file to download.
        dest_folder (str): The destination folder where the file should be saved.
    
    Returns:
        str: The local path to the downloaded file.
    """
    local_filename = os.path.join(dest_folder, urlparse(url).path.split('/')[-1])

    if os.path.exists(local_filename):
        print(f'{local_filename} already exists, skipping download')
        return local_filename

    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename

def convert_audio_to_wav(input_file, output_file):
    """
    Converts an audio file to WAV format with the required settings for transcription.
    
    Args:
        input_file (str): The path to the input audio file.
        output_file (str): The path to the output WAV file.
    """
    if os.path.exists(output_file):
        print(f'{output_file} already exists, skipping conversion')
        return
    subprocess.run([
        'ffmpeg', '-i', input_file,
        '-acodec', 'pcm_s16le',
        '-ac', '1',
        '-ar', str(FRAME_RATE),
        output_file
    ])
