m main:
	uvicorn main:app --reload
u uv_main:
    uv run uvicorn main:app

c container:
	podman build -t yt-downloader . && podman run --rm -p 8000:8000 -v "$(PWD)/out_dir:/app/out_dir:Z" --name yt-downloader-container yt-downloader
 
# python -m venv .venv
# source .venv/bin/activate

