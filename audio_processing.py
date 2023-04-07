import json
import os
import wave
from pyannote.audio import Pipeline
from config import PYANNOTE_ACCESS_TOKEN, FRAME_RATE
from download import download_file, convert_audio_to_wav
from google_drive import upload_to_google

def perform_speaker_diarization(conn, episode_id, input_file, num_speakers=None, min_speakers=None, max_speakers=None):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM diarization_results WHERE episode_id = ?", (episode_id,))
    if cursor.fetchone():
        print(f'Diarization results for episode {episode_id} already exist, skipping diarization')
        return

    # Instantiate pre-trained speaker diarization pipeline
    diarization_pipeline = Pipeline.from_pretrained(
        "pyannote/speaker-diarization",
        use_auth_token=PYANNOTE_ACCESS_TOKEN,
    )

    # Apply the pre-trained pipeline
    diarization = diarization_pipeline(
        input_file,
        num_speakers=num_speakers,
        min_speakers=min_speakers,
        max_speakers=max_speakers
    )

    for segment, _, speaker_id in diarization.itertracks(yield_label=True):
        start_time = segment.start
        end_time = segment.end
        duration = end_time - start_time

        cursor.execute("""
            INSERT INTO diarization_results (episode_id, speaker_id, start_time, end_time, duration)
            VALUES (?, ?, ?, ?, ?)
        """, (episode_id, speaker_id, start_time, end_time, duration))

    conn.commit()

def transcribe_audio(conn, episode_id, input_file, recognizer):
    """
    Transcribes the given audio file using Vosk and saves the transcription to the database.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        episode_id (int): The ID of the episode in the database.
        input_file (str): The path to the input audio file.
        recognizer (vosk.KaldiRecognizer): The Vosk recognizer object.

    Returns:
        list: The list of transcribed words with their timings and speaker ID placeholders.
    """
    print(f'Checking for existing transcription for episode ID {episode_id}')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT word, start_time, end_time, speaker_id
        FROM transcription_results
        WHERE episode_id = ?
        ORDER BY start_time
    """, (episode_id,))
    existing_transcription = cursor.fetchall()

    if existing_transcription:
        print(f'Transcription for episode ID {episode_id} already exists in the database, skipping transcription')
        return [dict(zip(["word", "start", "end", "speaker_id"], row)) for row in existing_transcription]

    with wave.open(input_file, "rb") as wf:
        total_frames = wf.getnframes()
        frame_position = 0
        transcription = []

        while frame_position < total_frames:
            # Read one minute of audio at a time
            num_frames = min(FRAME_RATE * 60, total_frames - frame_position)
            data = wf.readframes(num_frames)
            frame_position += num_frames

            # Reset the recognizer for each one-minute segment
            recognizer.Reset()

            # Accept the waveform data
            recognizer.AcceptWaveform(data)

            # Get the result
            result_dict = json.loads(recognizer.Result())

            # Extract the words and their timings
            words = result_dict.get("result", [])
            for word in words:
                word_info = {
                    'word': word['word'],
                    'start': word['start'],
                    'end': word['end'],
                    'speaker_id': -1  # Initialize with a placeholder value
                }
                transcription.append(word_info)

                cursor.execute("""
                    INSERT INTO transcription_results (episode_id, word, start_time, end_time, speaker_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (episode_id, word_info['word'], word_info['start'], word_info['end'], word_info['speaker_id']))

    conn.commit()
    # print(f'transcription:', transcription)
    return transcription

def format_transcript(punctuator, raw_transcript):
    """
    Formats a raw transcript by adding punctuation using the Punctuator model.

    Args:
        punctuator (punctuator.Punctuator): The Punctuator object.
        raw_transcript (str): The raw transcript without punctuation.

    Returns:
        str: The formatted transcript with punctuation.
    """
    if not raw_transcript.strip():  # Add this line to check if the input is empty
        return ""  # Return an empty string if the input is empty

    formatted_transcript = punctuator.punctuate(raw_transcript)
    return formatted_transcript

def assign_words_to_speakers(conn, episode_id, words):
    """
    Assigns words to speakers based on the speaker diarization information.

    Args:
        conn (sqlite3.Connection): The SQLite database connection.
        episode_id (int): The ID of the episode in the database.
        words (list): The list of words and their timings from the transcription.

    Returns:
        list: A list of dictionaries containing speaker IDs and their associated words.
    """
    cursor = conn.cursor()
    cursor.execute("""
        SELECT speaker_id, start_time, end_time
        FROM diarization_results
        WHERE episode_id = ?
        ORDER BY start_time
    """, (episode_id,))
    speaker_segments = cursor.fetchall()

    speaker_word_list = []

    for word in words:
        word_start_time = float(word['start'])
        assigned = False
        for segment in speaker_segments:
            speaker_id, start_time, end_time = segment
            if start_time <= word_start_time < end_time:
                if not speaker_word_list or speaker_word_list[-1]["speaker_id"] != speaker_id:
                    speaker_word_list.append({"speaker_id": speaker_id, "words": []})
                speaker_word_list[-1]["words"].append(word)
                assigned = True
                break

        if not assigned:
            if not speaker_word_list:
                # Assign the unassigned word(s) at the beginning of the transcript to the first speaker
                speaker_word_list.append({"speaker_id": speaker_segments[0][0], "words": [word]})
            else:
                # Assign the unassigned word to the last speaker segment
                speaker_word_list[-1]["words"].append(word)

    return speaker_word_list

def write_transcripts(conn, episode_id, speaker_word_list, punctuator, episode_title, episode_date):
    transcript_parts = []

    for speaker_entry in speaker_word_list:
        speaker_id = speaker_entry["speaker_id"]
        words = speaker_entry["words"]
        transcript = ' '.join([word['word'] for word in words])
        formatted_transcript = format_transcript(punctuator, transcript)

        start_time = words[0]['start']
        start_time_str = f"{int(start_time // 60)}:{int(start_time % 60):02d}"
        transcript_parts.append(f"[{start_time_str}] {speaker_id}: {formatted_transcript}")

    transcript_text = f"Episode Title: {episode_title}\nDate: {episode_date}\n\n" + "\n\n".join(transcript_parts)

    print(f'transcript_text: {transcript_text}')

    cursor = conn.cursor()
    cursor.execute("UPDATE transcripts SET transcript = ? WHERE id = ?", (transcript_text, episode_id))
    conn.commit()

def process_episode(item, downloads_dir, conn, recognizer, punctuator, num_speakers=None, min_speakers=None, max_speakers=None, upload_to_google_drive=False, overwrite=False):
    """
    Process a single podcast episode from the RSS feed by downloading the audio, transcribing it, and performing speaker diarization.

    Args:
        item (bs4.element.Tag): A BeautifulSoup object representing an <item> tag in the RSS feed.
        downloads_dir (str): Directory where downloaded audio files will be saved.
        conn (sqlite3.Connection): The SQLite database connection.
        recognizer (vosk.KaldiRecognizer): The Vosk recognizer object.
        punctuator (punctuator.Punctuator): The Punctuator object.
        num_speakers (int, optional): Number of speakers in the audio (if known).
        min_speakers (int, optional): Minimum number of speakers in the audio.
        max_speakers (int, optional): Maximum number of speakers in the audio.
        upload_to_google_drive (bool, optional): Whether or not to upload the transcript to google.
    """
    episode_date = item.find('pubDate').text.strip()
    episode_title = item.find('title').text.strip()
    enclosure = item.find('enclosure')

    mp3_url = enclosure['url']
    print(f'Downloading {mp3_url} to {downloads_dir}')
    mp3_file = download_file(mp3_url, downloads_dir)
    wav_file = os.path.splitext(mp3_file)[0] + '.wav'

    print(f'Converting {mp3_file} to {wav_file}')
    convert_audio_to_wav(mp3_file, wav_file)

    if enclosure and enclosure['type'].startswith('audio/mpeg'):
        episode_exists_query = "SELECT id, transcript FROM transcripts WHERE episode_title = ? AND episode_date = ?"
        cursor = conn.cursor()
        cursor.execute(episode_exists_query, (episode_title, episode_date))
        episode_exists = cursor.fetchone()

    if episode_exists:
        episode_id, existing_transcript = episode_exists
        if existing_transcript and existing_transcript.strip() and not overwrite:
            print(f"Transcript for '{episode_title}' already exists in the database, skipping transcription")
            return
        elif overwrite:
            print(f"Overwriting transcript for '{episode_title}'")
            cursor.execute("DELETE FROM transcription_results WHERE episode_id = ?", (episode_id,))
            cursor.execute("DELETE FROM diarization_results WHERE episode_id = ?", (episode_id,))
        else:
            print(f"Updating empty transcript for '{episode_title}'")
    else:
        print(f"Inserting {episode_title} into the database")
        cursor.execute("INSERT INTO transcripts (episode_title, episode_date, episode_wav_filename) VALUES (?, ?, ?)", (episode_title, episode_date, os.path.basename(wav_file)))
        conn.commit()
        episode_id = cursor.lastrowid

    print(f'Transcribing {wav_file}')
    words = transcribe_audio(conn, episode_id, wav_file, recognizer)

    print(f'Performing speaker diarization on {wav_file}')
    perform_speaker_diarization(
        conn,
        episode_id,
        wav_file,
        num_speakers=num_speakers,
        min_speakers=min_speakers,
        max_speakers=max_speakers
    )

    print(f'Assigning words to speakers')
    speaker_word_dict = assign_words_to_speakers(conn, episode_id, words)

    print(f'Writing transcripts for {episode_title} to the database')
    write_transcripts(conn, episode_id, speaker_word_dict, punctuator, episode_title, episode_date)

    if upload_to_google_drive:
        upload_to_google(conn, episode_id, episode_title, overwrite)
