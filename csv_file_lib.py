import csv
from application_logging import logger

class csv_methods:

    def __init__(self):
        self.file_object = open('application_logs/applicationLog.txt', 'a+')
        self.log_writer = logger.Application_logger()


    def create_csv_file(self, csv_file_name):
        with open(csv_file_name, 'w', encoding='utf-8', newline='') as csv_file:
            self.log_writer.log(self.file_object, "Created CSV file")
            return csv_file

    def initialize_csv_writter(self, csv_file):
        csv_writer = csv.writer(csv_file)
        return csv_writer

    def insert_record_in_csv(self, csv_writer, record):
        self.log_writer.log(self.file_object, "Adding record to CSV file")
        csv_writer.writerow(record)
