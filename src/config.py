"""
config.py

Set up configuration, logging, and checks.
"""
import datetime
import logging
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from icecream import install

install()

from rich.traceback import install
from rich.logging import RichHandler

log_level = logging.INFO

use_rich_traceback = False
sys.tracebacklimit = 1
if use_rich_traceback:
    install(show_locals=False)

# Disable requests library logging
logging.getLogger("requests").setLevel(logging.WARNING)

# root directories
root_dir = Path(__file__).parent.parent
book_dir = root_dir / "book"
out_dir = root_dir / "out"
log_dir = root_dir / "logs"

if not log_dir.exists():
    print(f"Creating log directory at {log_dir}...")
    log_dir.mkdir(exist_ok=True)

log_filename = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".log"

# set up logger
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[
        RichHandler(
            markup=True,
            show_level=False,
            show_time=False,
            show_path=False,
            level=log_level,
        ),
        logging.FileHandler(log_dir / log_filename)
    ],
)


# paths
@dataclass(frozen=True)
class Paths:
    root_dir: Path = root_dir

    book_dir: Path = book_dir
    content_dir: Path = book_dir / "content"
    outline_tex: Path = book_dir / "outline.tex"
    outline_json: Path = book_dir / "outline.json"
    index_tex: Path = book_dir / "index.tex"

    out_dir: Path = out_dir
    index_idx: Path = out_dir / "index.idx"


paths = Paths()

# check if the outline exists
if not paths.outline_json.exists():
    raise FileNotFoundError(
        f"Outline JSON file {paths.outline_json} does not exist. "
        "Please create it before running the script."
    )

# tex engine
tex_engine = "lualatex"

# check if tex engine is installed
try:
    command = [tex_engine, "--version"]
    subprocess.run(command, check=True, capture_output=True)
except FileNotFoundError:
    raise EnvironmentError(
        f"{tex_engine} is not installed or not found in PATH. "
        "Please install it before running the script."
    )

model_config = {
    "model": "claude-sonnet-4-0",
    "model_provider": "anthropic",
    "temperature": 0.8,
}
