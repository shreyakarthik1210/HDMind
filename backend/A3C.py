import argparse
import pylsl
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import threading
import numpy as np

# MongoDB setup
cluster = MongoClient("mongodb+srv://Admin:Pass@dataserver.cush8dg.mongodb.net/?retryWrites=true&w=majority")
db = cluster["HackUTD"]
collection = db["HDMind"]

# Argument parser
parser = argparse.ArgumentParser()
parser.add_argument('-n', '--stream_name', type=str, required=True,
                    default='PetalStream_eeg', help='the name of the LSL stream')
args = parser.parse_args()

# Function to preprocess data
def preprocess_data(sample):
    return np.array(sample)

# A3C Worker
class Worker(threading.Thread):
    def __init__(self, worker_id):
        super(Worker, self).__init__()
        self.worker_id = worker_id
        self.stop_signal = False

    def run(self):
        print("Worker %d started" % self.worker_id)
        while not self.stop_signal:
            sample, timestamp = inlet.pull_sample()
            processed_sample = preprocess_data(sample)
            # Perform A3C algorithm training here
            print("Worker %d processed sample: %s" % (self.worker_id, processed_sample))
            collection.insert_one({"WorkerID": self.worker_id, "Sample": processed_sample})
        print("Worker %d stopped" % self.worker_id)

# Main function
def main():
    # Resolve LSL stream
    print(f'Looking for a stream with name {args.stream_name}...')
    streams = pylsl.resolve_stream('name', args.stream_name)
    if len(streams) == 0:
        raise RuntimeError(f'Found no LSL streams with name {args.stream_name}')
    global inlet
    inlet = pylsl.StreamInlet(streams[0])

    # Create and start A3C workers
    num_workers = 4 
    workers = []
    for i in range(num_workers):
        worker = Worker(i)
        workers.append(worker)
        worker.start()

    try:
        # Keep the main thread alive
        while True:
            pass
    except KeyboardInterrupt:
        print("Stopping workers...")
        for worker in workers:
            worker.stop_signal = True
        for worker in workers:
            worker.join()

if __name__ == "__main__":
    main()
