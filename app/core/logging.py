# app/core/logging.py
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Optional


class JSONFormatter(logging.Formatter):
	"""
	Minimal JSON formatter for production logging
	Output one JSON object per line
	"""

	def format(self, record: logging.LogRecord) -> str:
		payload: dict[str, Any] = {
			"ts": datetime.now(timezone.utc).isoformat(),
			"level": record.levelname,
			"logger": record.name,
			"msg": record.getMessage(),
		}

		# Add exception info if available
		if record.exc_info:
			payload["exc_info"] = self.formatException(record.exc_info)

		# Support extra fields: logger.info("...", extra={"foo": "bar"}
		# Only include safe/serializable extras
		for key, value in record.__dict__.items():
			if key in (
					"name", "msg", "args", "levelname", "levelno", "pathname", "filename",
					"module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
					"created", "msecs", "relativeCreated", "thread", "threadName",
					"processName", "process"
			):
				continue
			if key.startswith("_"):
				continue
			try:
				json.dumps(value)
				payload[key] = value
			except TypeError:
				payload[key] = str(value)

		return json.dumps(payload, ensure_ascii=False)


def setup_logging(*, log_level: str = "INFO") -> None:
	"""
	Configure root logging exactly once
	Call this during application startup (lifespan event)
	"""
	level = getattr(logging, log_level.upper(), logging.INFO)

	root = logging.getLogger()
	root.setLevel(level)

	# Remove default handler, IMPORTANT when running under reload()
	root.handlers.clear()

	handler = logging.StreamHandler(sys.stdout)
	handler.setLevel(level)
	handler.setFormatter(JSONFormatter())
	root.addHandler(handler)

	# OPTIONAL here: remove noise from very chatty libraries
	logging.getLogger("uvicorn.access").setLevel(level)
	logging.getLogger("uvicorn.error").setLevel(level)


def get_logger(name: Optional[str] = None) -> logging.Logger:
	"""
	Get a logger instance. Use module-level logger like:
		logger = get_logger(__name__)
	"""
	return logging.getLogger(name if name else "opspilot")