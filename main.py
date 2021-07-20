import requests
from gtts import gTTS
from pydub import AudioSegment
from mutagen.mp3 import MP3
import moviepy.video.io.ImageSequenceClip
import moviepy.editor as mpe
from PIL import Image, ImageDraw, ImageFilter

# change this to your output directory
output_dir = "C:/Users/phone/PycharmProjects/automemer/output/"

# requires ffmpeg downloads
AudioSegment.converter = r"C:\Users\phone\PycharmProjects\automemer\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\Users\phone\PycharmProjects\automemer\ffprobe.exe"

total_memes = 40

def get_posts():
    base_url = "https://api.pushshift.io/reddit/search/submission/?subreddit=memes&sort=desc&sort_type=score&after=1d&size=" + str(total_memes)

    request = requests.get(base_url)
    return request.json()

def main():
    print("Starting Bot...")

    # we have to fetch all the latest posts from pushshift

    posts = get_posts()

    """FOR EACH MEME:"""

    counter = 0
    path_to_main_speech = output_dir + "video/" + "main.mp3"

    print("Parsing Posts...")

    for post in posts["data"]:
        if not "preview" in post:
            # no image preview
            continue

        title = post["title"]

        if not title or len(title) <= 3:
            title = "haha"

        image_url = post['preview']["images"][0]["source"]["url"]
        image_url = image_url.replace('amp;s', 's')

        path_to_image = output_dir + "posts/" + str(counter) + ".jpg"
        path_to_speech = output_dir + "posts/" + str(counter) + ".mp3"

        """Download the image"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0'
        }

        response = requests.get(image_url, headers=headers)

        with open(path_to_image, "wb") as handle:
            handle.write(response.content)

        # then we have to draw it onto a fixed canvas so all images are the same size
        try:
            image1 = Image.open(path_to_image)
        except:
            print("Skipping Image, cannot open")
            continue
        background = Image.open("C:/Users/phone/PycharmProjects/automemer/white.jpg")

        width, height = image1.size

        scale_factor = 1080/height

        width *= scale_factor
        height *= scale_factor

        new_size = (int(width), int(height))

        image1 = image1.resize(new_size)

        b_width, b_height = background.size

        background.paste(image1, (int(b_width/2) - int(width/2), 0)) # paste it in center

        background.save(path_to_image)

        # we have to use some text to speech library to read the title and have an mp3

        speech = gTTS(text=title, lang="en", slow=False)
        speech.save(path_to_speech)

        print("Finished processing: " + str(counter + 1) + " memes")

        counter += 1

    # lastly, we turn it all into a video
    video_output = output_dir + "video/" + "redditmemes.mp4"
    fps = 1
    image_files = []

    combined = AudioSegment.empty()

    print("Preparing Video + Audio")
    for i in range(counter):
        voice_over_path = output_dir + "posts/" + str(i) + ".mp3"

        voice_over = AudioSegment.from_mp3(voice_over_path)
        voice_over_length = MP3(voice_over_path).info.length  # pretty sure this is in seconds

        # add silence
        silence_duration = (1000 - ((voice_over_length * 1000) % 1000)) + 4000  # make the mp3 length a multiple of 1000
        silence = AudioSegment.silent(duration=silence_duration)
        voice_over += silence

        combined += voice_over

        total_seconds = int(silence_duration/1000 + voice_over_length)

        image_path = output_dir + "posts/" + str(i) + ".jpg"

        print(str(total_seconds) + "s video. generating frames...")
        for k in (range(total_seconds)):
            image_files.append(image_path)

        print("Prepared: " + str(i + 1) + "/" + str(counter))

    print("Finished preparing Video + Audio... Generating Video")
    combined.export(path_to_main_speech, format="mp3")
    video = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(image_files, fps=fps)

    audio_overlay = mpe.AudioFileClip(path_to_main_speech)

    pydub_music = AudioSegment.from_mp3("C:/Users/phone/PycharmProjects/automemer/backgroundmusic.mp3")
    pydub_background = pydub_music[:combined.duration_seconds]
    pydub_background.export(output_dir + "video/background.mp3")

    background_music = mpe.AudioFileClip(output_dir + "video/background.mp3")

    final_audio = mpe.CompositeAudioClip([audio_overlay, background_music])

    final_video = video.set_audio(final_audio)
    final_video.write_videofile(video_output, fps=fps)
    print("Finished!")

main()