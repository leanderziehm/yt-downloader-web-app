m main:
	uvicorn main:app --reload

c container:
	podman build -t yt-downloader . && podman run --rm -p 8000:8000 -v "$(PWD)/out_dir:/app/out_dir:Z" --name yt-downloader-container yt-downloader


# 	podman build -t yt-downloader . && podman run --rm -p 8000:8000 -v "$(pwd)/outdir:/app/outdir:Z" --name yt-downloader-container yt-downloader 
# m main:
# 	.venv/bin/python

# source .venv/bin/activate

run:
	uv run main.py


