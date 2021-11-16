import pyodbc
import json
import struct
import math
import random
import logging
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta


def get_config(config_file_path="config.json"):
    with open(config_file_path, "r") as config:
        return json.loads(config.read())


def get_random_number(min_value=0, max_value=100, decimal_points=2):
    return round(random.uniform(min_value, max_value), decimal_points)


def get_random_smallint():
    return get_random_number(-2 ** 15, 2 ** 15 - 1, 0)


def get_random_time():
    """
    returns random date object in range of last day
    :return:
    """
    return datetime.now() - timedelta(minutes=random.randrange(1440))  # reduce randomly 1440min (1d) from now


def handle_datetime2(dt2_value):
    tup = struct.unpack("<6hI", dt2_value)  # e.g., (2017, 5, 30, 8, 59, 37, 0, 665039700)
    return datetime(tup[0], tup[1], tup[2],
                    hour=tup[3], minute=tup[4], second=tup[5],
                    microsecond=math.floor(tup[6] / 1000.0 + 0.5))


def get_logger(logger_name=__name__, level=logging.DEBUG):
    log_formatter = logging.Formatter(fmt='%(asctime)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    log = logging.getLogger(logger_name)
    log.setLevel(level)
    # log_file = os.path.join(workspace, "{}.log".format(logger_name))
    # print("Log is at '{}'".format(log_file))
    # log_file_handler = logging.FileHandler(log_file)
    # log_file_handler.setFormatter(log_formatter)
    # log_file_handler.setLevel(level)
    # log.addHandler(log_file_handler)

    ch = logging.StreamHandler()
    ch.setLevel(level=level)
    ch.setFormatter(log_formatter)
    log.addHandler(ch)

    return log


def create_table(cursor):
    print("Create table")
    cursor.execute(
        "CREATE TABLE MachineScoreEvents(EventId INT IDENTITY(1,1) PRIMARY KEY CLUSTERED, MachineId UNIQUEIDENTIFIER, Score DECIMAL(5,2), MachineGroup SMALLINT, ReportTime DATETIME2(7), CONSTRAINT CHK_MachineScoreEvents_Score CHECK (Score>=0 AND Score<=100))")
    cursor.commit()


def drop_table(cursor):
    print("Drop table")
    cursor.execute("DROP TABLE IF EXISTS MachineScoreEvents")
    cursor.commit()


def reset_table():
    connection = get_connection()
    cursor = connection.cursor()
    drop_table(cursor)
    create_table(cursor)
    cursor.close()
    connection.close()


def get_connection():
    connection = pyodbc.connect(
        'DRIVER=' + config['driver'] + ';SERVER=tcp:' + config['server'] + ';PORT=1433;DATABASE=' + config[
            'database'] + ';UID=' + config['username'] + ';PWD=' + config['password'])
    connection.add_output_converter(pyodbc.SQL_TYPE_TIMESTAMP, handle_datetime2)
    return connection


def add_records(thread_number):
    global logger, items_per_thread
    connection = get_connection()
    cur = connection.cursor()
    cur.fast_executemany = True
    logger.debug(f"Starting {thread_number * items_per_thread}-{((thread_number + 1) * items_per_thread) - 1}")
    for i in range(items_per_thread):
        group = groups[int(get_random_number(0, 99, 0))]
        machine_id = uuid.uuid4()
        score = get_random_number()
        report_time = get_random_time()
        cur.execute(
            "INSERT INTO MachineScoreEvents (MachineId,Score,MachineGroup,ReportTime) values(?,?,?,?)",
            machine_id, score, group, report_time)
    logger.debug(f"Commit {thread_number * items_per_thread}-{((thread_number + 1) * items_per_thread) - 1}")
    cur.commit()
    cur.close()
    connection.close()


logger = get_logger()
num_of_threads = 20
items_to_populate = 1000000
items_per_thread = 100
groups = [get_random_smallint() for i in range(100)]
config = get_config()


# with pyodbc.connect(
#         'DRIVER=' + config['driver'] + ';SERVER=tcp:' + config['server'] + ';PORT=1433;DATABASE=' + config[
#             'database'] + ';UID=' + config['username'] + ';PWD=' + config['password']) as conn:
#     conn.add_output_converter(pyodbc.SQL_TYPE_TIMESTAMP, handle_datetime2)
#     with conn.cursor() as cursor:
#         create_table(cursor)
#         drop_table(cursor)
#         cursor.fast_executemany = True
#         for i in range(items_to_populate):
#             group = groups[int(get_random_number(0, 99, 0))]
#             cursor.execute(
#                 "INSERT INTO MachineScoreEvents (MachineId,Score,MachineGroup,ReportTime) values(?,?,?,?)",
#                 uuid.uuid4(), get_random_number(), group, get_random_time())
#             if i > 0 and i % 1000 == 0:
#                 logger.debug(f"Committing {i}/{items_to_populate}")
#                 cursor.commit()
#         cursor.commit()

def main():
    try:
        reset_table()

        # add_records(cursor, 1000, groups)
        with ThreadPoolExecutor(max_workers=num_of_threads) as executor:
            threads_count = int(items_to_populate / items_per_thread)
            print(f"Should run {threads_count} threads")
            for i in range(threads_count):
                executor.submit(add_records, thread_number=i)
            executor.shutdown(wait=True)
    except Exception as e:
        print(str(e))
    finally:
        pass


if __name__ == '__main__':
    main()
