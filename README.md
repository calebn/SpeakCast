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

* [pyannote.audio GitHub Repository](https://github.com/pyannote/pyannote-audio)
* [Vosk GitHub Repository](https://github.com/alphacep/vosk-api)
* [punctuator GitHub Repository](https://github.com/ottokart/punctuator)

## Configuration

To set up your configuration file, follow these steps:

1. Create a new file called `config.py` in the project root directory.
2. Copy the contents from the `config_example.py` file into `config.py`.
3. Replace the placeholder values with the appropriate information for your setup.

### Pyannote Access Token

To obtain a Pyannote access token, follow these steps:

1. Visit [hf.co/pyannote/speaker-diarization](https://huggingface.co/pyannote/speaker-diarization) and [hf.co/pyannote/segmentation](https://huggingface.co/pyannote/segmentation) and accept user conditions if requested.
2. Visit [hf.co/settings/tokens](https://huggingface.co/settings/tokens) to create an access token.
3. Add the created token to the `PYANNOTE_ACCESS_TOKEN` field in `config.py`.

### Punctuator Model

1. Download the Punctuator model (e.g., 'INTERSPEECH-T-BRNN.pcl') from the [Punctuator GitHub Repository](https://github.com/ottokart/punctuator).
2. Update the `PUNCTUATOR_MODEL_PATH` variable in `config.py` with the path to the downloaded model.

### Vosk Model

1. Download a Vosk model from the [Vosk model repository](https://alphacephei.com/vosk/models) and unzip it.
2. Update the `VOSK_MODEL_PATH` variable in `config.py` with the path to the unzipped model directory.

### Google Access Token and Email (optional)

If you want to enable uploading transcripts to Google Docs, follow these steps:

1. Update the `GOOGLE_ACCESS_TOKEN_JSON_PATH` variable in `config.py` with the path to your Google access token JSON file.
2. Update the `GOOGLE_DOC_WRITER_EMAIL` variable in `config.py` with the email address that should have writer access to the Google Docs.


## Usage

Run the script with the following command:

```
- <rss_file_or_url>: Path to the RSS file or URL (required when not using --print_urls, --export_diarization, --export_transcription, or --print_transcript options)
- -n <num_speakers>: Number of speakers (default is to estimate automatically) (optional)
- -m <min_speakers>: Minimum number of speakers to try (optional)
- -x <max_speakers>: Maximum number of speakers to try (optional)
- -g: Enable uploading transcripts to Google Docs (default is False) (optional)
- --overwrite: Overwrite existing information in the database (optional)
- -p: Print Google Doc URLs for all episodes or a specific episode (optional)
- --export_diarization: Export diarization results to RTTM format (used with -e and -d options)
- --export_transcription: Export transcription results to JSON format (used with -e and -d options)
- --print_transcript: Print episode transcript (used with -e and -d options)
- -d <podcast_dir>: Podcast directory to locate the correct transcripts.db file (required when using --print_urls, --export_diarization, --export_transcription, or --print_transcript options)
- -e <episode_title>: Specify the episode title for exporting, printing, or processing (required when using --print_urls, --export_diarization, --export_transcription, or --print_transcript options)
- -w <wav_file>: Specify a single wav file to transcribe only (optional)
```

## Example Usage

`python main.py "https://example.com/rss.xml"`

This command will download all episodes in the RSS feed and generate transcripts for them

`python main.py "https://example.com/rss.xml" -e "Interesting Episode" -n 2 -g`

This command will download and process only the episode with "Interesting Episode" in its title from the RSS feed at "https://example.com/rss.xml", it designates that there are two speakers and creates a new Google Doc with the transcript

`python main.py --print_transcript -d <podcast_dir> -e <episode_title>`

This command will print a previously created transcript for the supplied podcast directory with the supplied episode title

`python main.py --export_diarization -e "Episode Title" -d some_podcast_dir > output_diarization.rttm`

This command will print the speaker diarization results for the supplied Episode in the supplied podcast directory as an [rttm](https://github.com/nryant/dscore#rttm) file.

`python main.py -w "path/to/your_wav_file.wav"`

This command will transcribe the specified .wav file and print the transcription to the console.


## License

[MIT License](https://opensource.org/license/mit/)
