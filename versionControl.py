from pymongo import MongoClient
import selfPwd
from datetime import datetime
import subprocess

class versionControl(): 
    version = "2.1"

    def updateversion(self):
        conn = MongoClient(selfPwd.getMongoUrl())
        db = conn.simcorpfinder

        collection = db['version']
        data = {
            "version":self.version,
            "updateInfo":"Add some shorcuts(News, Website and Documentation) on the app interface.",
            "time":datetime.utcnow()
        }
        collection.insert_one(data)

if __name__ == "__main__":
    v = versionControl()
    v.updateversion()
    # subprocess.run(["D:\\Projects\\venvs\\simcorpfinder\\Scripts\\python", "setup.py", "bdist_msi"])