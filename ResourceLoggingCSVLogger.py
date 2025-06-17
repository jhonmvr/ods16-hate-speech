import os
import csv
import json
import psutil
from datetime import datetime
from tensorflow.keras.callbacks import Callback

try:
    import GPUtil
    GPU_AVAILABLE = True
except ImportError:
    GPU_AVAILABLE = False

class ResourceLoggingCSVLogger(Callback):
    def __init__(self, csv_filename='training_log.csv', jsonl_filename='epoch_logs.jsonl', append=False):
        super().__init__()
        self.csv_filename = csv_filename
        self.jsonl_filename = jsonl_filename
        self.append = append
        self.writer = None
        self.csv_file = None
        self.keys = None

    def on_train_begin(self, logs=None):
        mode = 'a' if self.append else 'w'
        self.csv_file = open(self.csv_filename, mode, newline='')
        self.writer = None
        if not self.append and os.path.exists(self.jsonl_filename):
            os.remove(self.jsonl_filename)

    def get_resource_usage(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        gpu_load, gpu_mem = None, None
        if GPU_AVAILABLE:
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu_load = gpus[0].load * 100
                    gpu_mem = gpus[0].memoryUtil * 100
            except:
                pass
        return cpu, mem, gpu_load, gpu_mem

    def on_epoch_end(self, epoch, logs=None):
        logs = logs or {}
        cpu, mem, gpu, gpu_mem = self.get_resource_usage()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        full_logs = {
            'epoch': epoch,
            'timestamp': timestamp,
            'cpu_percent': cpu,
            'ram_percent': mem,
            'gpu_percent': gpu if gpu is not None else 'N/A',
            'gpu_memory_percent': gpu_mem if gpu_mem is not None else 'N/A',
        }
        full_logs.update(logs)

        if self.writer is None:
            self.keys = list(full_logs.keys())
            self.writer = csv.DictWriter(self.csv_file, fieldnames=self.keys)
            if not self.append or os.stat(self.csv_filename).st_size == 0:
                self.writer.writeheader()

        self.writer.writerow(full_logs)
        self.csv_file.flush()

        with open(self.jsonl_filename, 'a') as jf:
            json.dump(full_logs, jf)
            jf.write('\n')

    def on_train_end(self, logs=None):
        self.csv_file.close()
