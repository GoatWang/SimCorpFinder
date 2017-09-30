from pymongo import MongoClient
import selfPwd
from datetime import datetime
import subprocess

class versionControl(): 
    version = "2.0"

    def updateversion(self):
        conn = MongoClient(selfPwd.getMongoUrl())
        db = conn.simcorpfinder

        collection = db['version']
        data = {
            "version":self.version,
            "updateInfo":"We update the algorithm and database. Sorry, you must update to this version to continue to use this product.",
            "time":datetime.utcnow()
        }
        collection.insert_one(data)

if __name__ == "__main__":
    v = versionControl()
    v.updateversion()
    # subprocess.run(["D:\\Projects\\venvs\\simcorpfinder\\Scripts\\python", "setup.py", "bdist_msi"])