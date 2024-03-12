# MariaDB MaxScale Docker image

## Running
[The MaxScale docker-compose setup](./docker-compose.yml) contains MaxScale
configured with 2 sharded database servers, populates them with data from shard1.sql and shard2.sql, and launches a maxscale instance for routing queries between them. 
It also creates a user in each database names "maxuser" and gives it all the necessary permissions to act as the monitor and router using the init.sql scripts present in each folder of the maxscale/sql directory. 

To start, run the following commands in the maxscale-docker/maxscale directory

```
docker-compose up -d
```

After MaxScale and the servers have started (takes a few minutes), you can find
the schema router's listener on port 4000. The user `maxuser` with the password `maxpwd` can be used to test the cluster.

Assuming the mariadb client is installed on the host machine:
```
$ mysql -umaxuser -pmaxpwd -h 127.0.0.1 -P 4000
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MySQL connection id is 5
Server version: 10.2.12 2.2.9-maxscale mariadb.org binary distribution

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

MySQL [None]>
```
You can edit the [`maxscale.cnf.d/example.cnf`](./maxscale.cnf.d/example.cnf)
file and recreate the MaxScale container to change the configuration.

To stop the containers, execute the following command. Optionally, use the -v
flag to also remove the volumes.

To run maxctrl in the container to see the status of the cluster:
```
$ docker-compose exec maxscale maxctrl list servers
```
Output should look like this:
```
┌─────────┬─────────┬──────┬─────────────┬─────────────────┬──────────┐
│ Server  │ Address │ Port │ Connections │ State           │ GTID     │
├─────────┼─────────┼──────┼─────────────┼─────────────────┼──────────┤
│ shard1  │ shard1  │ 3306 │ 0           │ Master, Running │ 0-3000-5 │
├─────────┼─────────┼──────┼─────────────┼─────────────────┼──────────┤
│ shard2  │ shard2  │ 3306 │ 0           │        Running  │ 0-3000-5 │
├─────────┼─────────┼──────┼─────────────┼─────────────────┼──────────┤
```

## Testing
You can test the databases and the schema router by running the queries.py script with the following command

```
python queries.py
```

This script sends 4 queries to the listener on port 4000, two that query each database individually, and two more that query both databases.
If you receive output with no errors then everything is working properly. Congratulations!

Once complete, to remove the cluster and maxscale containers:

```
docker-compose down -v
```

## docker-compose.yml

This file defines a docker-compose configuration for two running MariaDB instances and a MaxScale instance to serve as a database proxy for sharding.

**For the databases**:
```
        image: mariadb:10.3
```

This specifies the Docker image to be used for the service, which is mariadb:10.3.

```
MYSQL_ALLOW_EMPTY_PASSWORD: 'Y'
```

This allows the MySQL root user to have an empty password. (Not recommended, but makes granting permissions easy to do)

```
 volumes:
            - ./sql/shard1:/docker-entrypoint-initdb.d
```

This mounts the ./sql/shard1 local directory to the /docker-entrypoint-initdb.d directory inside the container. 
This allows initializing the MySQL database with scripts placed in ./sql/shard1 when the container starts.

```
command: mysqld --log-bin=mariadb-bin --binlog-format=ROW --server-id=3001
```

This specifies the command to be run when the container starts. 
It starts MySQL with enabled binary logging (--log-bin=mariadb-bin), setting the binary log format to row-based replication (--binlog-format=ROW), and assigning a unique server ID (--server-id=3001).

```
ports:
            - "4002:3306"
```

This maps port 3306 inside the container to port 4002 on the host machine, allowing connections to MySQL on shard1 service from port 4002 on the host.

**For the MaxScale instance:**
```
image: mariadb/maxscale:latest
```
This defines the maxscale service, which uses the mariadb/maxscale Docker image.

```
depends_on:
           - shard1
           - shard2
```

This specifies that the maxscale service depends on the shard1 and shard2 services, ensuring they are started before maxscale.

```
volumes:
            - ./maxscale.cnf.d:/etc/maxscale.cnf.d
```

 This mounts the local directory ./maxscale.cnf.d to /etc/maxscale.cnf.d inside the container, allowing MaxScale to use the configuration files from the host.

```
ports:
            - "4000:4000"  # sharded-service listener.
            - "8989:8989"  # REST API port
```

 This maps port 4000 on the host to port 4000 inside the container for the sharded-service listener, allowing external applications to connect to MaxScale. It also maps port 8989 on the host to port 8989 inside the container for the REST API.

## example.cnf

This file defines the configuration for two shard servers (shard1 and shard2), a sharded service that routes queries to these servers based on the schema, a listener for client connections to the sharded service, and a monitor to monitor the health of the shard servers.

```
[shard1]
type=server
address=shard1
port=3306
protocol=MariaDBBackend
```

[shard1]: This is the section header defining the configuration for the first shard server.

type=server: Specifies that this configuration block represents a database server.

address=shard1: Specifies the hostname, you can use an IP address here instead if needed.

port=3306: Specifies the port on which the first shard server is listening for database connections.

protocol=MariaDBBackend: Specifies the protocol used for communication with the first shard server, which is MariaDB in this case.

```
[Sharded-Service]
type=service
router=schemarouter
servers=shard1,shard2
user=maxuser
password=maxpwd
```

[Sharded-Service]: This is the section header defining the configuration for the sharded service.

type=service: Specifies that this configuration block represents a service.

router=schemarouter: Specifies the router plugin used for routing queries to the appropriate servers based on the schema.

servers=shard1,shard2: Specifies the list of servers included in this service. Queries routed to this service will be distributed among these servers.

user=maxuser and password=maxpwd: Specifies the credentials used to authenticate connections to the servers.

```
[Sharded-Service-Listener]
type=listener
service=Sharded-Service
protocol=mariadbclient
port=4000
```

[Sharded-Service-Listener]: This is the section header defining the configuration for the listener of the sharded service.

type=listener: Specifies that this configuration block represents a listener.

service=Sharded-Service: Specifies the service to which this listener is associated.

protocol=mariadbclient: Specifies the protocol used by clients to connect to this listener, which is MariaDB client protocol.

port=4000: Specifies the port on which this listener is listening for client connections.

```
[MySQL-Monitor]
type=monitor
module=mariadbmon
servers=shard1,shard2
user=maxuser
password=maxpwd
```
[MySQL-Monitor]: This is the section header defining the configuration for the monitor.

type=monitor: Specifies that this configuration block represents a monitor.

module=mariadbmon: Specifies the monitoring module used for monitoring the health of the servers.

servers=shard1,shard2: Specifies the list of servers to be monitored.

user=maxuser and password=maxpwd: Specifies the credentials used to authenticate connections for monitoring purposes.

## queries.py 

This script connects to databases via the sharded listener and queries them with maxuser to make sure that this profile has been given the proper grants and the databases have been populated.

```
def connect_one(query):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port='4000', # Listener is mapped on port 4000
            user='maxuser',
            password='maxpwd',
        )

        cursor = connection.cursor()

        # Execute USE statement to select the zipcodes_one database
        cursor.execute("USE zipcodes_one")

        cursor.execute(query)
        rows = cursor.fetchall()

        return rows

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
```

The connect functions are used to execute queries on their respective databases using the sharded listener.
Since we are running all of this on the same machine It connects to the service running on 127.0.0.1 with port 4000, using the username maxuser and password maxpwd.
It then executes the provided query using a cursor and fetches all the rows returned by the query.
The finally-block ensures that the cursor and connection are closed, even if an exception occurs.

```
def query_two():
    try:
        # All zipcodes where state=KY (Kentucky)
        zipcodes_one = connect_one("SELECT zipcode FROM zipcodes_one WHERE State='KY';")
        zipcodes_two = connect_two("SELECT zipcode FROM zipcodes_two WHERE State='KY';")

        # Combine the results from both databases
        all_zipcodes = zipcodes_one + zipcodes_two

        # Print the combined results
        print("All zipcodes where state=KY (Kentucky):")

        for row in all_zipcodes:
            print(row)

    except Exception as e:
        # Print error message if an exception occurs
        print("Error:", e)
```

The queries retrieve data from one or both databases. In this case query_two is querying both databases for all the zipcodes in the state of Kentucky.
It calls a connect function for each database to execute its queries for each one respectively, it then combines the results and prints the output.

## Init.sql

This script is ran on both database servers when they are launched, it creates a user named maxuser and allows it to connect from any IP address. (This is **NOT** secure, but is suitable for this project for simplicity's sake)
Once maxuser is created the script grants it all the permissions it needs to act as the monitor and the schema router. (This is also **NOT** secure)

```
CREATE USER 'maxuser'@'%' IDENTIFIED BY 'maxpwd';
```

Creates maxuser, allows it to log in from any IP or host, and assigns maxpwd as its password.

```
GRANT SELECT ON mysql.user TO 'maxuser'@'%';
GRANT SELECT ON mysql.db TO 'maxuser'@'%';
GRANT SELECT ON mysql.tables_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.columns_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.procs_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.proxies_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.roles_mapping TO 'maxuser'@'%';
GRANT SHOW DATABASES ON *.* TO 'maxuser'@'%';
GRANT SELECT ON mysql.* TO 'maxuser'@'%';
```

These are all the permissions that are necessary for maxuser to act as the monitor. Without these, your MySQL-Monitor will have authentication errors.

```
GRANT SELECT, REPLICATION SLAVE, INSERT, UPDATE, USAGE, DELETE ON *.* TO 'maxuser'@'%';
```

This line grants maxuser all the permissions it needs as the schema router to authorize or perform read, write, update, delete etc. on the databases.
Technically queries.py should only need SELECT and USAGE to work since it only reads data and does not modify, add, or remove it. However, these extra permissions give you more freedom to play around with things.

```
FLUSH PRIVILEGES;
```

This line reloads the privileges from the grants tables so that the above changes go into effect right away.

## Reference material:

Here are some links that I used to help me make this configuration and provide better insight on sharding.

**Permissions references**
https://mariadb.com/kb/en/mariadb-maxscale-2308-mariadb-monitor/#required-grants

https://mariadb.com/kb/en/mariadb-maxscale-6-setting-up-mariadb-maxscale/

**Configuration references**
https://mariadb.com/kb/en/mariadb-maxscale-6-configuring-servers/

https://mariadb.com/kb/en/mariadb-maxscale-6-simple-sharding-with-two-servers/

**More on sharding**
https://www.digitalocean.com/community/tutorials/understanding-database-sharding
