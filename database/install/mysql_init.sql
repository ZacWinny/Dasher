-- create database
CREATE DATABASE IF NOT EXISTS delivery;
USE delivery;

-- create customers table
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    membership_status ENUM('Bronze', 'Silver', 'Gold', 'Platinum') NOT NULL DEFAULT 'Bronze'
);

-- create restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    category varchar(255) null,
    contact varchar(20) not null,
    revenue DECIMAL(10, 2) DEFAULT 0,

);

-- create menu_items table
CREATE TABLE IF NOT EXISTS menu_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(5, 2) NOT NULL,
    restaurant_id INT,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- create orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    restaurant_id INT,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id)
);

-- create order_items table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    menu_item_id INT,
    quantity INT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (menu_item_id) REFERENCES menu_items(id)
);
create table if not exists feedback(
    id int auto_increment primary key,
    customer_id int,
    restaurant_id int,
    feedback varchar(255),
    datetime timestamp default current_timestamp,
    rating int,
    foreign key (customer_id) references customers(id),
    foreign key (restaurant_id) references restaurants(id)
);

create table if not exist revenue_report(
    id int auto_increment primary key,
    restaurant_id int,
    revenue decimal(10,2),
    report_date date,
    foreign key (restaurant_id) references restaurants(id)
);

-- create client user
CREATE USER IF NOT EXISTS 'client'@'%' IDENTIFIED BY 'client';
GRANT DELETE, INSERT, UPDATE, SELECT ON delivery.* TO 'client'@'%';
FLUSH PRIVILEGES;