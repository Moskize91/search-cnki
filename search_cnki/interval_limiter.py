import time
import threading

# thread safe object
class IntervalLimiter:
  def __init__(self, interval: float):
    self._interval = interval
    self._lock: threading.Lock = threading.Lock()
    self._last_time = 0.0

  def limit(self):
    with self._lock:
      current_time = time.time()
      sleep_duration: int = self._interval - (current_time - self._last_time)

    if sleep_duration > 0:
      time.sleep(sleep_duration)

    with self._lock:
      self._last_time = time.time()
