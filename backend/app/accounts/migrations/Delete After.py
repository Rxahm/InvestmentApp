import moviepy.editor as mp
from pydub import AudioSegment, effects
import whisper
import os

# Step 1: Extract audio from video
def extract_audio(video_path, output_audio_path):
    video = mp.VideoFileClip("C:\\Users\\rabiu\\Videos\\May 19th\\IMG_6145.mov")
    video.audio.write_audiofile(r"C:\Users\rabiu\Videos\May 19th\output_audio.wav", codec='pcm_s16le')

# Step 2: Enhance audio (normalize volume)
def enhance_audio(input_audio_path, output_enhanced_path):
    audio = AudioSegment.from_file(r"C:\Users\rabiu\Videos\May 19th\output_audio.wav")
    normalized_audio = effects.normalize(audio)
    normalized_audio.export(output_enhanced_path, format="wav")

# Step 3: Transcribe with Whisper
def transcribe_audio(audio_path, model_size="base"):
    model = whisper.load_model(model_size)
    result = model.transcribe(audio_path)
    return result['text']

# Runner
video_file = "input_video.mp4"
raw_audio = "raw_audio.wav"
enhanced_audio = "enhanced_audio.wav"

extract_audio(video_file, raw_audio)
enhance_audio(raw_audio, enhanced_audio)
transcription = transcribe_audio(enhanced_audio)

print("Transcription:\n", transcription)
