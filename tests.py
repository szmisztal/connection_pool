from connection_pool import ConnectionPool
import threading
import time

def connection_pool_test(thread_id):
    try:
        connection = connection_pool.get_connection()
        query = '''SELECT * FROM users'''
        connection.cursor.execute(query)
        result = connection.cursor.fetchall()
        print(f"{thread_id} - {result}")
        connection_pool.release_connection(connection)
    except Exception as e:
        print(f"{thread_id} - {e}")


connection_pool = ConnectionPool(10, 100)
threads = []
test_duration_seconds = 300

start_time = time.time()
while (time.time() - start_time) < test_duration_seconds:
    thread = threading.Thread(target = connection_pool_test, args = [len(threads)])
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()
