import time

class IntervalLimiter:
  def __init__(self, interval: float):
    self.interval = interval
    self.last_time = 0.0

  def limit(self):
    current_time = time.time()
    if current_time < self.last_time + self.interval:
      time.sleep(self.interval - (current_time - self.last_time))
      self.last_time = time.time()
    else:
      self.last_time = current_time
