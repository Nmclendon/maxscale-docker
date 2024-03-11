CREATE USER 'maxuser'@'%' IDENTIFIED BY 'maxpwd';

GRANT SELECT ON mysql.user TO 'maxuser'@'%';
GRANT SELECT ON mysql.db TO 'maxuser'@'%';
GRANT SELECT ON mysql.tables_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.columns_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.procs_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.proxies_priv TO 'maxuser'@'%';
GRANT SELECT ON mysql.roles_mapping TO 'maxuser'@'%';
GRANT SHOW DATABASES ON *.* TO 'maxuser'@'%';
GRANT SELECT ON mysql.* TO 'maxuser'@'%';

GRANT SELECT, REPLICATION SLAVE, UPDATE, USAGE, DELETE ON *.* TO 'maxuser'@'%';

FLUSH PRIVILEGES;
