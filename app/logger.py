from __future__ import annotations

import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "output" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

run_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
log_file = LOG_DIR / f"run_{run_stamp}.log"

logger = logging.getLogger("smart-learning-lab-blog")
logger.setLevel(getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO))
logger.handlers.clear()

formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

console = logging.StreamHandler(sys.stdout)
console.setFormatter(formatter)
logger.addHandler(console)

file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

logger.info("Logging initialized: %s", log_file)
