#!/bin/bash

# Check if mysql is installed
if [ -z "$(which mysql)" ]; then
    sudo apt update
    echo "Installing mysql..."
    sudo apt-get install mysql-server -y
    sudo mysql_secure_installation
    # initialise user and delivery database
    sudo service mysql start
    sudo mysql -u root -p < database/install/mysql_init.sql
    echo "mysql installed successfully"

else
    echo "mysql is already installed"
fi

# Check if mysql is running
if [ -z "$(pgrep mysql)" ]; then
    echo "Starting mysql..."
    sudo service mysql start
else
    echo "mysql is already running"
fi