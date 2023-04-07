# Fill in the values and save as config.py

# Access Token
# Replace with your Hugging Face Pyannote access token (see: https://huggingface.co/pyannote/ for details)
# 1. visit hf.co/pyannote/speaker-diarization and hf.co/pyannote/segmentation and accept user conditions (only if requested)
# 2. visit hf.co/settings/tokens to create an access token (only if you had to go through 1.)
# 3/ visit https://huggingface.co/settings/tokens, create a token and add it here
# If this fails, check https://github.com/pyannote/pyannote-audio for changed instructions
PYANNOTE_ACCESS_TOKEN = "your_pyannote_access_token_here"

# Punctuator Model Path
# Replace with the path to the downloaded Punctuator model (e.g., 'INTERSPEECH-T-BRNN.pcl')
PUNCTUATOR_MODEL_PATH = "path_to_punctuator_model_here"

# Vosk Model Path
# Replace with the path to the downloaded Vosk model (e.g., 'vosk-model-en-us-0.42-gigaspeech', see https://alphacephei.com/vosk/models)
VOSK_MODEL_PATH = "path_to_vosk_model_here"

# Audio Frame Rate
# You can keep this as 16000, as it's a standard frame rate for processing audio files
FRAME_RATE = 16000

# Google Access Token JSON Path
GOOGLE_ACCESS_TOKEN_JSON_PATH = 'some_token.json'

# Google Doc Email that will get Writer Access
GOOGLE_DOC_WRITER_EMAIL = 'some-email@example.com'
