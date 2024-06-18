from moviepy.editor import ImageClip, concatenate_videoclips, concatenate_audioclips, AudioFileClip
import requests
from PIL import Image
from io import BytesIO
import os
from gtts import gTTS

def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(BytesIO(response.content))
        image_path = f"{image_url.split('/')[-1]}.png"
        image.save(image_path)
        return image_path
    else:
        raise Exception(f"Failed to download image from {image_url}")

def generate_narration(text, output_file, lang='en'):
    print(f"Generating narration for text: {text} with language: {lang}")  # Debug info
    tts = gTTS(text, lang=lang)
    tts.save(output_file)
    print(f"Narration saved to {output_file}")  # Debug info

def create_movie(image_urls, narrations, voices, output_file="output_video.mp4", fps=24):
    clips = []
    audio_clips = []
    
    for i, image_url in enumerate(image_urls):
        # Download the image
        image_path = download_image(image_url)
        print(f"Downloaded image {i+1}: {image_path}")  # Debug info

        # Generate narration audio
        narration = narrations[i]
        speaker = list(voices.keys())[i % len(voices)]  # Assign voice to the speaker
        voice_lang = voices[speaker]
        audio_file = f"narration_{i}.mp3"
        generate_narration(narration, audio_file, lang=voice_lang)
        audio_clip = AudioFileClip(audio_file)
        audio_duration = audio_clip.duration
        audio_clips.append(audio_clip.set_duration(audio_duration))
        print(f"Generated narration {i+1}: {audio_file} with duration {audio_duration}")  # Debug info

        # Create an ImageClip for each image
        image_clip = ImageClip(image_path).set_duration(audio_duration)
        clips.append(image_clip)
    
    # Concatenate all the video clips
    video = concatenate_videoclips(clips, method="compose")
    # Concatenate all the audio clips
    audio = concatenate_audioclips(audio_clips)
    
    # Set audio to the video
    final_video = video.set_audio(audio)
    # Write the result to a file with fps specified
    final_video.write_videofile(output_file, codec="libx264", fps=fps)
    print(f"Video written to {output_file}")  # Debug info

    # Clean up audio files
    for i in range(len(audio_clips)):
        os.remove(f"narration_{i}.mp3")



# from moviepy.editor import ImageClip, concatenate_videoclips, concatenate_audioclips, AudioFileClip
# import requests
# from PIL import Image
# from io import BytesIO
# import os
# from gtts import gTTS
# from pydub import AudioSegment

# def download_image(image_url):
#     response = requests.get(image_url)
#     if response.status_code == 200:
#         image = Image.open(BytesIO(response.content))
#         image_path = f"{image_url.split('/')[-1]}.png"
#         image.save(image_path)
#         return image_path
#     else:
#         raise Exception(f"Failed to download image from {image_url}")

# def generate_narration(text, output_file, lang='en'):
#     print(f"Generating narration for text: {text}")  # Debug info
#     tts = gTTS(text, lang=lang)
#     tts.save(output_file)
#     print(f"Narration saved to {output_file}")  # Debug info

# def create_movie(image_urls, narrations, voices, output_file="output_video.mp4", fps=24):
#     clips = []
#     audio_clips = []
    
#     for i, image_url in enumerate(image_urls):
#         # Download the image
#         image_path = download_image(image_url)
#         print(f"Downloaded image {i+1}: {image_path}")  # Debug info

#         # Generate narration audio
#         narration = narrations[i]
#         audio_file = f"narration_{i}.mp3"
#         generate_narration(narration, audio_file, lang='en')
#         audio_clip = AudioFileClip(audio_file)
#         audio_duration = audio_clip.duration
#         audio_clips.append(audio_clip.set_duration(audio_duration))
#         print(f"Generated narration {i+1}: {audio_file} with duration {audio_duration}")  # Debug info

#         # Create an ImageClip for each image
#         image_clip = ImageClip(image_path).set_duration(audio_duration)
#         clips.append(image_clip)
    
#     # Concatenate all the video clips
#     video = concatenate_videoclips(clips, method="compose")
#     # Concatenate all the audio clips
#     audio = concatenate_audioclips(audio_clips)
    
#     # Set audio to the video
#     final_video = video.set_audio(audio)
#     # Write the result to a file with fps specified
#     final_video.write_videofile(output_file, codec="libx264", fps=fps)
#     print(f"Video written to {output_file}")  # Debug info

#     # Clean up audio files
#     for i in range(len(audio_clips)):
#         os.remove(f"narration_{i}.mp3")
