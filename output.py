import json

def print_google_doc_urls(conn, episode_title=None):
    cursor = conn.cursor()
    if episode_title:
        cursor.execute("SELECT episode_title, doc_link FROM transcripts WHERE episode_title LIKE ? AND doc_link IS NOT NULL", (f"%{episode_title}%",))
    else:
        cursor.execute("SELECT episode_title, doc_link FROM transcripts WHERE doc_link IS NOT NULL")

    results = cursor.fetchall()
    if not results:
        print("No Google Doc URLs found.")
        return

    print("Google Doc URLs:")
    for title, doc_link in results:
        print(f"{title}: {doc_link}")

def print_diarization_as_rttm(conn, episode_title):
    cursor = conn.cursor()
    cursor.execute("SELECT id, episode_wave_filename FROM transcripts WHERE episode_title = ?", (episode_title,))
    result = cursor.fetchone()

    if result:
        episode_id = result[0]
        wav_filename = result[1]
        cursor.execute("SELECT * FROM diarization_results WHERE episode_id = ? ORDER BY start_time", (episode_id,))
        diarization_results = cursor.fetchall()

        for result in diarization_results:
            print(f"SPEAKER {wav_filename} 1 {result[3]} {result[5]} <NA> <NA> {result[2]} <NA> <NA>")
    else:
        print(f"No diarization results found for episode '{episode_title}'.")

def print_transcription_as_json(conn, episode_title):
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM transcripts WHERE episode_title = ?", (episode_title,))
    result = cursor.fetchone()

    if result:
        episode_id = result[0]
        cursor.execute("SELECT * FROM transcription_results WHERE episode_id = ? ORDER BY start_time", (episode_id,))
        transcription_results = cursor.fetchall()

        json_data = []
        for result in transcription_results:
            json_data.append({
                "word": result[2],
                "start_time": result[3],
                "end_time": result[4],
                "speaker_id": result[5]
            })

        print(json.dumps(json_data, indent=2))
    else:
        print(f"No transcription results found for episode '{episode_title}'.")

def print_episode_transcript(conn, episode_title):
    cursor = conn.cursor()
    cursor.execute("SELECT transcript FROM transcripts WHERE episode_title = ?", (episode_title,))
    result = cursor.fetchone()

    if result:
        transcript = result[0]
        print(transcript)
    else:
        print(f"No transcript found for episode '{episode_title}'.")
