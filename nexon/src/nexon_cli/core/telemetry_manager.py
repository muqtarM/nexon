import json
import threading
import time
from queue import Queue, Empty

from nexon_cli.core.configs import config
from nexon_cli.utils.logger import logger
import requests


class TelemetryManager:
    """
    Sends anonymized usage events to a telemetry endpoint or Segment.
    Events are queued and sent in a background thread.
    """

    def __init__(self):
        self.endpoint = config.telemetry_url  # e.g. https://telemetry.mycompany.com/collect
        self.api_key = config.telemetry_api_key
        self.enabled = getattr(config, "telemetry_enabled", False)
        self.queue = Queue()
        self.thread = None

        if self.enabled and self.endpoint:
            self.thread = threading.Thread(target=self._worker, daemon=True)
            self.thread.start()
            logger.info("Telemetry thread started")
        else:
            logger.info("Telemetry disabled (no endpoint or disabled).")

    def _worker(self):
        while True:
            try:
                event = self.queue.get(timeout=5)
            except Empty:
                continue
            try:
                headers = {'Content-Type': 'application/json'}
                if self.api_key:
                    headers['Authorization'] = f"Bearer {self.api_key}"
                requests.post(self.endpoint, json=event, headers=headers, timeout=5)
            except Exception as e:
                logger.error(f"Telemetry send failed: {e}")
            finally:
                self.queue.task_done()

    def send_event(self, event_name: str, properties: dict = None):
        """
        Queue an event for sending.
        """
        if not self.enabled or not self.endpoint:
            return
        event = {
            "event": event_name,
            "timestamp": time.time(),
            "properties": properties or {}
        }
        self.queue.put(event)


# Singleton
telemetry_manager = TelemetryManager()
