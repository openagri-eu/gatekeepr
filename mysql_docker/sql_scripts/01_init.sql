CREATE DATABASE IF NOT EXISTS gatekeeper;
ALTER DATABASE gatekeeper CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'gatekeeper_admin'@'%' IDENTIFIED BY 'asdasdasd';
GRANT ALL PRIVILEGES ON gatekeeper.* TO 'gatekeeper_admin'@'%';
FLUSH PRIVILEGES;
