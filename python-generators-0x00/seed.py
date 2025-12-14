#!/usr/bin/python3
import mysql.connector
from mysql.connector import Error
import csv
import uuid


def connect_db():
    """Connect to MySQL server (without specifying database)."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_password'  # 🔁 Replace with your MySQL password
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def create_database(connection):
    """Create the ALX_prodev database if it doesn’t exist."""
    try:
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev;")
        print("Database ALX_prodev created or already exists.")
    except Error as e:
        print(f"Error creating database: {e}")
    finally:
        cursor.close()


def connect_to_prodev():
    """Connect to ALX_prodev database."""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='Evan@..6100.',  # 🔁 Replace with your MySQL password
            database='ALX_prodev'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to ALX_prodev: {e}")
        return None


def create_table(connection):
    """Create the user_data table if not exists."""
    try:
        cursor = connection.cursor()
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id CHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL(3,0) NOT NULL,
            INDEX (user_id)
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        print("Table user_data created successfully")
    except Error as e:
        print(f"Error creating table: {e}")
    finally:
        cursor.close()


def insert_data(connection, csv_file):
    """Insert data into user_data table from CSV file."""
    try:
        cursor = connection.cursor()

        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                user_id = str(uuid.uuid4())
                name = row['name']
                email = row['email']
                age = row['age']

                # Check if email already exists
                cursor.execute("SELECT email FROM user_data WHERE email = %s", (email,))
                result = cursor.fetchone()

                if not result:
                    cursor.execute("""
                        INSERT INTO user_data (user_id, name, email, age)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, name, email, age))

        connection.commit()
        print("Data inserted successfully from CSV file.")
    except Error as e:
        print(f"Error inserting data: {e}")
    finally:
        cursor.close()
