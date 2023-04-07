# Podcast Transcription and Speaker Diarization

This script downloads, transcribes, and performs speaker diarization on podcast episodes from an RSS feed. It also supports uploading transcripts to Google Docs and printing Google Doc URLs for transcripts.

## Installation

### Set up pyannote environment

Create a new conda environment and activate it:

```
conda create -n pyannote python=3.8
conda activate pyannote
```

Install PyTorch 1.11, torchvision, and torchaudio:

`conda install pytorch==1.11.0 torchvision==0.12.0 torchaudio==0.11.0 -c pytorch`

Install required libraries

`pip install pyannote.audio beautifulsoup4 requests vosk punctuator google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client`

[pyannote.audio GitHub Repository](https://github.com/pyannote/pyannote-audio)
[Vosk GitHub Repository](https://github.com/alphacep/vosk-api)
[punctuator GitHub Repository](https://github.com/ottokart/punctuator)

### Set up Vosk

1. Download a Vosk model from the [Vosk model repository](https://alphacephei.com/vosk/models) and unzip it.
2. Update the `VOSK_MODEL_PATH` variable in the `config.py` file to point to the unzipped model directory.

## Optionally Set Up Google Drive for Uploads

* Go to the [Google Cloud Console](https://console.cloud.google.com/).
* Create a new project or select an existing one.
* In the Dashboard, click on "Enable APIs and Services" and enable the Google Docs API and Google Drive API.
* Go to the "Credentials" tab and create credentials for a service account.
* Download the JSON key file for the service account (You will only be able to do this once).
* Update `GOOGLE_ACCESS_TOKEN_JSON_PATH` and `GOOGLE_DOC_WRITER_EMAIL` in `config.py`

## Usage

Run the script with the following command:

```
python main.py <rss_file_or_url> [-k <episode_title_keyword>] [-n <num_speakers>] [-m <min_speakers>] [-x <max_speakers>] [-g] [--overwrite] [--print_urls] [-e <episode_title>]

- <rss_file_or_url>: Path to the RSS file or URL
- -k <episode_title_keyword>: Process only the episode with the keyword in the title (optional)
- -n <num_speakers>: Number of speakers (default is to estimate automatically) (optional)
- -m <min_speakers>: Minimum number of speakers to try (optional)
- -x <max_speakers>: Maximum number of speakers to try (optional)
- -g: Enable uploading transcripts to Google Docs (default is False) (optional)
- --overwrite: Overwrite existing information in the database (optional)
- --print_urls: Print Google Doc URLs for all episodes or a specific episode (optional)
- -e <episode_title>: Print Google Doc URL for the specified episode title (used with --print_urls) (optional)
```


## Example Usage

`python main.py "https://example.com/rss.xml" -e "Interesting Episode" -n 2 -g`

This command will download and process only the episode with "Interesting Episode" in its title from the RSS feed at ""https://example.com/rss.xml"

`python main.py --export_diarization "Episode Title" -d some_podcast_dir > output_diarization.rttm`

This command will print the speaker diarization results for the supplied Episode in the supplied podcast directory as an [rttm](https://github.com/nryant/dscore#rttm) file.

## License

[MIT License](https://opensource.org/license/mit/)
