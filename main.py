import re
from pathlib import Path
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pytubefix import YouTube
from pytubefix.cli import on_progress

app = FastAPI()

OUTPUT_DIR = Path("out_dir")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def serve_index():
    return FileResponse("./static/index.html", media_type="text/html")


class FileRequest(BaseModel):
    filename: str


def filename_to_save(filename: str) -> str:
    """
    Sanitize a filename:
    - Keep ASCII characters only.
    - Replace spaces with underscores.
    - Remove URL-unsafe and filesystem-unsafe characters.
    - Preserve letters, digits, dots, underscores, and hyphens.
    - Prevent empty names and special directory names.
    """
    if not isinstance(filename, str):
        raise ValueError("Filename must be a string")

    # Use only the filename, not a directory path.
    if filename != filename.strip():
        raise ValueError("Filename cannot start or end with whitespace")

    if not filename or filename in (".", ".."):
        raise ValueError("Invalid filename")

    # Reject directory traversal and path separators.
    if "/" in filename or "\\" in filename:
        raise ValueError("Directory paths are not allowed")

    # Replace spaces with underscores.
    filename = filename.replace(" ", "_")

    # Keep ASCII letters, digits, dots, underscores, and hyphens.
    filename = re.sub(r"[^a-zA-Z0-9._-]", "", filename)

    # Avoid special directory names and empty filenames.
    if not filename or filename in (".", ".."):
        raise ValueError("Invalid filename")

    # Avoid hidden files and names beginning with a dot.
    filename = filename.lstrip(".")

    if not filename or filename in (".", ".."):
        raise ValueError("Invalid filename")

    # Limit filename length.
    filename = filename[:200]

    return filename


def get_file_path(filename: str) -> Path:
    """Return a safe file path inside OUTPUT_DIR, matching existing files if possible."""
    safe_name = filename_to_save(filename)
    output_dir = OUTPUT_DIR.resolve()

    for file_path in output_dir.iterdir():
        if filename_to_save(file_path.name) == safe_name:
            resolved_path = file_path.resolve()

            if not resolved_path.is_relative_to(output_dir):
                raise ValueError("Invalid filename")

            return resolved_path

    # No matching file exists; return the intended safe path.
    resolved_path = (output_dir / safe_name).resolve()

    if not resolved_path.is_relative_to(output_dir):
        raise ValueError("Invalid filename")

    return resolved_path

# def create_file(filename: str, out_dir: Path = OUTPUT_DIR) -> Path:
    # """Create a file using a sanitized filename."""
    # safe_name = filename_to_save(filename)
    # file_path = out_dir / safe_name

    # file_path.write_text("Hello World", encoding="utf-8")

    # return file_path

def create_file(url:str, out_dir: Path = OUTPUT_DIR) -> Path:
    yt = YouTube(url, on_progress_callback=on_progress)
    print(yt.title)
    ys = yt.streams.get_audio_only()
    outpath = ys.download(output_path=out_dir)
    return Path(outpath)

@app.post("/create-file")
def generate_file(request: FileRequest):
    try:
        file_path = create_file(request.filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except OSError:
        raise HTTPException(status_code=500, detail="Could not create file")

    if file_path == None:
        raise HTTPException(status_code=500, detail="Could not create file")
    # if file_path == None:
        # raise HTTPException(status_code=500, detail="Could not create file")

    return {
        "message": "File created successfully",
        "filename": file_path.name,
        "file_path": str(file_path),
        "file_id": file_path.name,
        "download_url": f"/download/{file_path.name}",
        "delete_url": f"/files/{file_path.name}",
    }


@app.get("/files")
def list_files():
    files = []

    for file_path in OUTPUT_DIR.iterdir():
        if not file_path.is_file():
            continue

        stat = file_path.stat()

        files.append({
            "filename": file_path.name,
            "file_id": file_path.name,
            "file_size_bytes": stat.st_size,
            "file_size_kb": round(stat.st_size / 1024, 2),
            "created_date": datetime.fromtimestamp(
                stat.st_ctime,
                tz=timezone.utc,
            ).isoformat(),
            "download_url": f"/download/{filename_to_save(file_path.name)}",
            "delete_url": f"/files/{file_path.name}",
        })

    return {
        "total_files": len(files),
        "files": files,
    }


@app.get("/download/{filename}")
def download_file(filename: str):
    try:
        file_path = get_file_path(filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@app.delete("/files/{filename}")
def delete_file(filename: str):
    """Delete a file from OUTPUT_DIR."""
    try:
        file_path = get_file_path(filename)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="File not found")

    try:
        file_path.unlink()
    except OSError:
        raise HTTPException(status_code=500, detail="Could not delete file")

    return {
        "message": "File deleted successfully",
        "filename": file_path.name,
        "file_id": file_path.name,
    }
