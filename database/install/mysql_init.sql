

-- create database
create database delivery;
-- create client user
create user 'client'@'localhost' identified by 'client';
grant delete, insert, update, select on delivery.* to 'client'@'localhost';
flush privileges;
