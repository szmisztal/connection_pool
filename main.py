import psycopg2
import schedule
from threading import Lock
from test_variables import user, password, host, port, database_name


class ConnectionPool:
    def __init__(self, min_numbers_of_connections, max_number_of_connections):
        self.connections_list = []
        self.connections_in_use_list = []
        self.lock = Lock()
        self.min_number_of_connections = min_numbers_of_connections
        self.max_number_of_connections = max_number_of_connections
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database_name = database_name
        self.create_start_connections()
        self.connections_manager()

    def connection_to_db(self):
        self.connection = psycopg2.connect(
            user = self.user,
            password = self.password,
            host = self.host,
            port = self.port,
            database = self.database_name
        )
        return self.connection

    def create_start_connections(self):
        for _ in range(self.min_number_of_connections):
            connection = self.connection_to_db()
            self.connections_list.append([connection, True])

    def get_connection(self):
        self.lock.acquire()
        try:
            for connection, is_free in self.connections_list:
                if is_free:
                    self.connections_in_use_list.append(connection)
                    self.connections_list.remove([connection, is_free])
                    return connection
            if len(self.connections_list) < self.max_number_of_connections \
                    and len(self.connections_list) + len(self.connections_in_use_list) < self.max_number_of_connections:
                new_connection = self.connection_to_db()
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
                self.connections_in_use_list.remove(connection)
                self.connections_list.append([connection, True])
        finally:
            self.lock.release()

    def destroy_unused_connections(self):
        self.lock.acquire()
        try:
            for connection in self.connections_list:
                if len(self.connections_list) > 11:
                    connection.close()
                    self.connections_list.remove([connection, True])
                    if len(self.connections_list) == 10:
                        break
        except:
            self.lock.release()

    def keep_connections_at_the_starting_level(self):
        if self.connections_list < self.min_number_of_connections:
            for _ in self.connections_list:
                connection = self.connection_to_db()
                self.connections_list.append([connection, True])
                if self.connections_list == self.min_number_of_connections:
                    break

    def connections_manager(self):
        schedule.every(1).minute.do(self.destroy_unused_connections)
        schedule.every(1).minute.do(self.keep_connections_at_the_starting_level)

    def test_query(self):
        connection = self.get_connection()
        cursor = connection.cursor()
        query = '''SELECT * FROM users'''
        cursor.execute(query)
        result = cursor.fetchall()
        print(result)
        self.release_connection(connection)

test = ConnectionPool(10, 100)
test.test_query()



