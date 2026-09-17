# install

```
git clone https://github.com/LeanderZiehm/yt-downloader-flask-web
cd yt-downloader-flask-web

```

# install on device
# run

```
pip install -r requirements.txt
python3 main.py
```

# install using docker / (podman)
```
podman build -t my-flask-app .
podman run --rm -p 5000:5000 my-flask-app
podman run -d --name my-flask-app -p 5000:5000 my-flask-app
```

# open

```
http://127.0.0.1:5000/
```

# Guide

Just copy the url of a youtube video you want to download then hit the download button. It will automatically download the video for you. (both to downloads in yt-downloader-flask-web and the browser downloads)

# Preview

![preview](docs/preview.png)



# todo 

add dowload playlist support 
add link list download in parallel
add progress for bulk downloading
