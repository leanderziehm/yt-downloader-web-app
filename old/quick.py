from pytubefix import YouTube
from pytubefix.cli import on_progress
from pathlib import Path

url = ""

def main():

    create_file()

def create_file(filename:str,out_dir="out_dir"):
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)
    ys = yt.streams.get_audio_only()
    ys.download(output_path=out_dir)



if __name__ == "__main__":
    main()