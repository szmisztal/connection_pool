import psycopg2
from threading import Lock
from test_variables import user, password, host, port, database_name


class ConnectionPool:
    def __init__(self, min_numbers_of_conns, max_number_of_cons):
        self.database = self.connection_to_db(
            user = user,
            password = password,
            host = host,
            port = port,
            database_name = database_name
            )
        self.connections_list = []
        self.connections_in_use = []
        self.lock = Lock()
        self.min_number_of_conns = min_numbers_of_conns
        self.max_number_of_conns = max_number_of_cons

    def connection_to_db(self, user, password, host, port, database_name):
        self.lock.acquire()
        self.connection = psycopg2.connect(
            user = user,
            password = password,
            host = host,
            port = port,
            database = database_name
        )
        self.lock.release()
        return self.connection

    def create_start_connections(self):
        self.lock.acquire()
        for _ in range(self.min_number_of_conns):
            connection = self.database
            self.connections_list.append([connection, True])
        self.lock.release()

