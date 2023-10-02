import psycopg2


connections_list = []
min_number_of_pools = 10
max_number_of_pools = 100

def connection_to_db(user, password, host, port, database):
    connection = psycopg2.connect(
        user = user,
        password = password,
        host = host,
        port = port,
        database = database
    )
    return connection

def create_connections_pool_with_app_start(number_of_pools, **kwargs):
    for _ in range(number_of_pools):
        connection = connection_to_db(**kwargs)
        connections_list.append(connection)
        if len(connections_list) >= min_number_of_pools:
            break

def check_number_of_active_connections(connections_list):
    if len(connections_list) < min_number_of_pools:
        static_number_of_pools = min_number_of_pools - len(connections_list)
        create_connections_pool_with_app_start(static_number_of_pools)
    elif len(connections_list) >= max_number_of_pools:
        print("Connections list full, try again later")
