import os
import speech_recognition as sr
from moviepy.video.io.VideoFileClip import VideoFileClip
from pydub import AudioSegment
from pydub.silence import split_on_silence

def detect_silence(audio, silence_thresh=-80, min_silence_len=500):
    silence_segments = []
    non_silence_segments = split_on_silence(
        audio, silence_thresh=silence_thresh, min_silence_len=min_silence_len)
    start_time = 0

    for segment in non_silence_segments:
        end_time = start_time + segment.duration_seconds
        silence_segments.append((start_time, end_time))
        start_time = end_time

    return silence_segments

def transcribe_video(video_path, output_dir):
    video_clip = VideoFileClip(video_path)
    audio_clip = video_clip.audio
    audio_path = os.path.join(output_dir, "audio.wav")
    audio_clip.write_audiofile(audio_path)

    audio = AudioSegment.from_wav(audio_path)
    silence_segments = detect_silence(audio)

    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio_data = recognizer.record(source)
        transcript = recognizer.recognize_google(audio_data)

    transcription_with_timestamps = []
    cumulative_duration = 0.0

    for i, sentence in enumerate(transcript.split('.')):
        if i < len(silence_segments):
            timestamp = (cumulative_duration + audio.duration_seconds) / 1000.0
            cumulative_duration += silence_segments[i][1] - silence_segments[i][0]
        else:
            timestamp = cumulative_duration + audio.duration_seconds / 1000.0

        timestamp_str = f"{timestamp:.3f}"
        transcription_with_timestamps.append(f"[{timestamp_str}] Speaker: {sentence.strip()}")

    output_file_path = os.path.join(output_dir, "transcription.txt")
    with open(output_file_path, 'w') as file:
        file.write('\n'.join(transcription_with_timestamps))

    return output_file_path
