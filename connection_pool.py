import psycopg2
import schedule
from threading import Lock
from variables import user, password, host, port, database_name

class Connection:
    def __init__(self):
        self.connection = psycopg2.connect(
            user = user,
            password = password,
            host = host,
            port = port,
            database = database_name
        )
        self.cursor = self.connection.cursor()
        self.in_use = False

class ConnectionPool:
    def __init__(self, min_numbers_of_connections, max_number_of_connections):
        self.connections_list = []
        self.connections_in_use_list = []
        self.lock = Lock()
        self.min_number_of_connections = min_numbers_of_connections
        self.max_number_of_connections = max_number_of_connections
        self.create_start_connections()
        self.connections_manager()

    def create_start_connections(self):
        for _ in range(self.min_number_of_connections):
            connection = Connection()
            self.connections_list.append(connection)

    def get_connection(self):
        self.lock.acquire()
        try:
            for connection in self.connections_list:
                if connection.in_use == False:
                    connection.in_use = True
                    self.connections_in_use_list.append(connection)
                    self.connections_list.remove(connection)
                    return connection
            if len(self.connections_list) < self.max_number_of_connections \
                    and len(self.connections_list) + len(self.connections_in_use_list) < self.max_number_of_connections:
                new_connection = Connection()
                new_connection.in_use = True
                self.connections_in_use_list.append(new_connection)
                return new_connection
            else:
                print("There are no free connections at the moment, please try again soon")
        finally:
            self.lock.release()

    def release_connection(self, connection):
        self.lock.acquire()
        try:
            if connection in self.connections_in_use_list:
                connection.in_use = False
                self.connections_list.append(connection)
                self.connections_in_use_list.remove(connection)
        finally:
            self.lock.release()

    def destroy_unused_connections(self):
        self.lock.acquire()
        try:
            for connection in self.connections_list:
                if len(self.connections_list) > 11:
                    connection.close()
                    self.connections_list.remove(connection)
                    if len(self.connections_list) == 10:
                        break
        finally:
            self.lock.release()

    def keep_connections_at_the_starting_level(self):
        if len(self.connections_list) < self.min_number_of_connections:
            for _ in self.connections_list:
                connection = Connection()
                self.connections_list.append(connection)
                if len(self.connections_list) == self.min_number_of_connections:
                    break

    def connections_manager(self):
        schedule.every(1).minute.do(self.destroy_unused_connections)
        schedule.every(1).minute.do(self.keep_connections_at_the_starting_level)





