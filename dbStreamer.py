'''
This script receives a Petal formatted LSL stream and prints it to the console.

Usage: python lsl_receive.py -n PetalStream_eeg
valid LSL stream names for use with petal streaming apps:
    * PetalStream_gyroscope
    * PetalStream_ppg
    * PetalStream_telemetry
    * PetalStream_eeg
    * PetalStream_acceleration
    * PetalStream_connection_status
'''
import argparse
import pylsl
import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


# uri = "mongodb+srv://Admin:Pass@dataserver.cush8dg.mongodb.net/?retryWrites=true&w=majority"
# # Create a new client and connect to the server
# client = MongoClient(uri, server_api=ServerApi('1'))
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)

cluster = MongoClient("mongodb+srv://Admin:Pass@dataserver.cush8dg.mongodb.net/?retryWrites=true&w=majority")
db = cluster["HackUTD"]
collection = db["HDMIND"]
# data1 = {"_id": 0, "name": "Rohith", "data": "test"}
# data2 = {"_id": 1, "name": "Shreya", "data": "test2"}
# data3 = {"_id": 2, "name": "Sri", "data": "test3"}

# collection.insert_many([data1, data2, data3])

parser = argparse.ArgumentParser()
parser.add_argument('-n', '--stream_name', type=str, required=True,
                    default='PetalStream_eeg', help='the name of the LSL stream')
args = parser.parse_args()

# first resolve an EEG stream
print(f'looking for a stream with name {args.stream_name}...')
streams = pylsl.resolve_stream('name', args.stream_name)

# create a new inlet to read from the stream
if len(streams) == 0:
    raise RuntimeError(f'Found no LSL streams with name {args.stream_name}')
inlet = pylsl.StreamInlet(streams[0])

while True:
    sample, timestamp = inlet.pull_sample()
    print(timestamp, sample)
    collection.insert_one({"_id": timestamp, "Delta": sample[0], "Theta": sample[1], "Alpha": sample[2], "Beta": sample[3], "Gamma": sample[4]})