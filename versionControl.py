from pymongo import MongoClient
import selfPwd
from datetime import datetime
import subprocess

class versionControl(): 
    version = "2.2"

    def updateversion(self):
        conn = MongoClient(selfPwd.getMongoUrl())
        db = conn.simcorpfinder

        updateInfo = "[bug fixed] lemmatize keywords!"

        collection = db['version']
        data = {
            "version":self.version,
            "updateInfo":updateInfo,
            "time":datetime.utcnow()
        }
        collection.insert_one(data)


        collection = db['news']
        data = {
            "news": "[v" + self.version + " updated]" + updateInfo,
            "time":datetime.utcnow()
        }
        collection.insert_one(data)

if __name__ == "__main__":
    v = versionControl()
    v.updateversion()
    # subprocess.run(["D:\\Projects\\venvs\\simcorpfinder\\Scripts\\python", "setup.py", "bdist_msi"])