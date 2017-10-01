from pymongo import MongoClient
import selfPwd
from datetime import datetime

conn = MongoClient(selfPwd.getMongoUrl())
db = conn.simcorpfinder

collection = db['news']
data = {
    "news":"Welcome to SimCorpFinder!",
    "time":datetime.utcnow()
}
collection.insert_one(data)