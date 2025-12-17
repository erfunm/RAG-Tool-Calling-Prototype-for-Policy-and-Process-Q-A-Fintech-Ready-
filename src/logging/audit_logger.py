"""Structured JSON logging for auditability."""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import yaml


def configure_logger(config_path: str = "configs/default.yaml") -> logging.Logger:
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    logging_cfg = cfg.get("logging", {})
    log_path = Path(logging_cfg.get("audit_log_path", "logs/audit.log"))
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("audit")
    logger.setLevel(logging_cfg.get("level", "INFO"))
    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def log_event(logger: logging.Logger, event_type: str, payload: Dict[str, Any]) -> None:
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "payload": payload,
    }
    logger.info(json.dumps(record))
