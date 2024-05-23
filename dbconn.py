import pymongo
import certifi
from bson.objectid import ObjectId
import credentials

def conn_to_db(): 
    oid = credentials.get_test_oid()
    client = pymongo.MongoClient(credentials.get_cred(), tlsCAFile=certifi.where())#, server_api=ServerApi('1'))
    db = client["Chore-bot-db"]


    return client
