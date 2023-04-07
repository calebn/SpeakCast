import os
import argparse
import re
import requests
import sys
from bs4 import BeautifulSoup
from punctuator import Punctuator
from urllib.parse import urlparse
from vosk import Model, KaldiRecognizer
from config import VOSK_MODEL_PATH, FRAME_RATE, PUNCTUATOR_MODEL_PATH
from database import create_database
from output import print_google_doc_urls, print_diarization_as_rttm, print_transcription_as_json, print_episode_transcript
from audio_processing import process_episode

def main(args):
    if args.podcast_dir:
        podcast_dir = args.podcast_dir
        conn = create_database(os.path.join(podcast_dir, "transcripts.db"))

    if args.print_urls:
        print_google_doc_urls(conn, args.episode_title)
        return

    if args.export_diarization:
        print_diarization_as_rttm(conn, args.episode_title)
        return

    if args.export_transcription:
        print_transcription_as_json(conn, args.episode_title)
        return

    if args.print_transcript:
        print_episode_transcript(conn, args.episode_title)
        return

    parsed_url = urlparse(args.rss_file_or_url)
    if parsed_url.scheme in ('http', 'https'):
        response = requests.get(args.rss_file_or_url)
        response.raise_for_status()
        rss_content = response.text
    else:
        with open(args.rss_file_or_url, 'r') as f:
            rss_content = f.read()

    soup = BeautifulSoup(rss_content, 'xml')
    podcast_title = soup.find('title').text.strip()
    podcast_title = re.sub(r'\W+', '_', podcast_title)

    podcast_dir = os.path.join(".", podcast_title)
    os.makedirs(podcast_dir, exist_ok=True)

    downloads_dir = os.path.join(podcast_dir, "downloads")
    transcripts_dir = os.path.join(podcast_dir, "transcripts")
    os.makedirs(downloads_dir, exist_ok=True)
    os.makedirs(transcripts_dir, exist_ok=True)
    conn = create_database(os.path.join(podcast_dir, "transcripts.db"))
    items = soup.find_all('item')

    model = Model(VOSK_MODEL_PATH)
    recognizer = KaldiRecognizer(model, FRAME_RATE)
    recognizer.SetWords(True)

    punctuator = Punctuator(PUNCTUATOR_MODEL_PATH)

    found = False

    for item in items:
        title = item.find('title').text.strip()
        if args.episode_title and args.episode_title.lower() not in title.lower():
            continue
        found = True
        process_episode(item, downloads_dir, conn, recognizer, punctuator, args.num_speakers, args.min_speakers, args.max_speakers, args.upload_to_google, args.overwrite)

    if not found and args.episode_title:
        print(f"Episode with keyword '{args.episode_title}' not found")
    elif not found:
        print("No episodes found with keyword(s) '{args.episode_title}'")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process podcast episodes and store transcriptions in the database.')
    parser.add_argument('rss_file_or_url', nargs='?', default='', help='Path to the RSS file or URL')
    parser.add_argument('-n', '--num_speakers', type=int, default=None, help='Number of speakers (default is to estimate automatically)')
    parser.add_argument('-m', '--min_speakers', type=int, default=None, help='Minimum number of speakers to try (default is None)')
    parser.add_argument('-x', '--max_speakers', type=int, default=None, help='Maximum number of speakers to try (default is None)')
    parser.add_argument('-g', '--upload_to_google', action='store_true', help='Enable uploading transcripts to Google Docs (default is False)')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing information in the database.')
    parser.add_argument('-p', '--print_urls', action='store_true', help='Print Google Doc URLs for all episodes or a specific episode')
    parser.add_argument('--export_diarization', action='store_true', help='Export diarization results to RTTM format')
    parser.add_argument('--export_transcription', action='store_true', help='Export transcription results to JSON format')
    parser.add_argument('--print_transcript', action='store_true', help='Print episode transcript')
    parser.add_argument('-d', '--podcast_dir', help='Podcast directory to locate the correct transcripts.db file')
    parser.add_argument('-e', '--episode_title', help='Specify the episode title for exporting, printing or processing')
    args = parser.parse_args()

    if args.num_speakers is not None and (args.min_speakers is not None or args.max_speakers is not None):
        print("Error: You cannot specify both num_speakers and min_speakers/max_speakers. Please choose one approach.")
        sys.exit(1)

    if not (args.print_urls or args.export_diarization or args.export_transcription or args.print_transcript) and not args.rss_file_or_url:
        print("Error: Please provide an RSS file or URL when not using the --print_urls, --export_diarization, --export_transcription, or --print_transcript options.")
        sys.exit(1)

    if (args.export_diarization or args.export_transcription or args.print_transcript) and not args.episode_title:
        print("Error: Please provide an episode title when using the --print_urls, --export_diarization, --export_transcription, or --print_transcript options.")
        sys.exit(1)

    if (args.print_urls or args.export_diarization or args.export_transcription or args.print_transcript) and not args.podcast_dir:
        print("Error: Please provide an episode title when using the --print_urls, --export_diarization, --export_transcription, or --print_transcript options.")
        sys.exit(1)

    main(args)
