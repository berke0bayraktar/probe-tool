from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json

from .scripts.ffprobe_utils import scan_directory

app = FastAPI()
#app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

DATA_DIR = "/data"

@app.get("/", response_class=HTMLResponse)
def get_form(request: Request):
    subdirs = [f.name for f in os.scandir(DATA_DIR) if f.is_dir()]
    return templates.TemplateResponse("index.html", {"request": request, "folders": subdirs})

@app.post("/scan", response_class=JSONResponse)
def run_probe(folder: str = Form(...)):
    target = os.path.join(DATA_DIR, folder)
    if not os.path.exists(target):
        return JSONResponse({"error": "Folder not found."}, status_code=404)

    results = scan_directory(target)
    out_path = os.path.join(target, "probe_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return {"message": "Scan complete", "output_file": out_path}
