import pymongo
from application_logging import logger


class db_connection:

    def __init__(self):
        self.file_object = open('application_logs/applicationLog.txt', 'a+')
        self.log_writer = logger.Application_logger()

    USER_NAME = 'sowmya'
    PASSWORD = '12341234'
    CONNECTION_URL = f"mongodb+srv://{USER_NAME}:{PASSWORD}@cluster0.g02qv.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
    DB_NAME = "flipkartData"

    def connect_mongoDB(self):
        client = pymongo.MongoClient(self.CONNECTION_URL)
        database = client[self.DB_NAME]
        self.log_writer.log(self.file_object,f'Connected to Mongo DB Atlas with DB: {self.DB_NAME}')
        return database

    def create_collection(self, database, collection_name):
        collection = database[collection_name]
        self.log_writer.log(self.file_object, f'Created collection: {collection_name}')
        return collection

    def check_existence_collection(self, database, collection_name):
        coll_list = database.list_collection_names()
        if collection_name in coll_list:
            self.log_writer.log(self.file_object, f"Collection name: {collection_name}, is exists")
            return True
        self.log_writer.log(self.file_object, f"Collection name: {collection_name}, is not exists")
        return False

    def get_records(self, collection):
        self.log_writer.log(self.file_object, f"Checking records existing in DB more than 500 or not")
        records_list = collection.find()
        return records_list

    def insert_single_record_to_db(self, collection, record):
        self.log_writer.log(self.file_object, "Inserting record to DB")
        record = collection.insert(record)

    def insert_multiple_records_to_db(self, collection, records):
        self.log_writer.log(self.file_object, "Inserting multiple records to DB")
        records = collection.insert_many(records)
