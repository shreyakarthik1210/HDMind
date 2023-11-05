import pymongo
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
cluster = MongoClient("mongodb+srv://Admin:Pass@dataserver.cush8dg.mongodb.net/?retryWrites=true&w=majority")
db = cluster["HackUTD"]
collection = db["HDMind"]
fig = plt.figure()
dx = fig.add_subplot(9, 1, 1)
tx = fig.add_subplot(9, 1, 3)
ax = fig.add_subplot(9, 1, 5)
bx = fig.add_subplot(9, 1, 7)
gx = fig.add_subplot(9, 1, 9)
x = []
y1 = []
y2 = []
y3 = []
y4 = []
y5 = []
for doc in collection.find():
    x.append(doc.get("_id"))
    y1.append(doc.get("Delta"))
    y2.append(doc.get("Theta"))
    y3.append(doc.get("Alpha"))
    y4.append(doc.get("Beta"))
    y5.append(doc.get("Gamma"))
dx.plot(x, y1)
tx.plot(x, y2)
ax.plot(x, y3)
bx.plot(x, y4)
gx.plot(x, y5)
dx.set_xlabel('Time')
dx.set_ylabel('Delta')
tx.set_xlabel('Time')
tx.set_ylabel('Theta')
ax.set_xlabel('Time')
ax.set_ylabel('Alpha')
bx.set_xlabel('Time')
bx.set_ylabel('Beta')
gx.set_xlabel('Time')
gx.set_ylabel('Gamma')
plt.show()