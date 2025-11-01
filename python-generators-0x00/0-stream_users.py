#!/usr/bin/python3
import mysql.connector

def stream_users():
    """
    Generator function that connects to the ALX_prodev database
    and streams rows from the user_data table one by one.
    Yields:
        dict: Each row as a dictionary containing user_id, name, email, and age
    """
    # Connect to the ALX_prodev database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Evan@..6100.",  
        database="ALX_prodev"
    )

    cursor = connection.cursor(dictionary=True)

    # Execute the query to select all users
    cursor.execute("SELECT user_id, name, email, age FROM user_data")

    # Use a single loop to yield one row at a time
    for row in cursor:
        yield row

    # Close cursor and connection when done
    cursor.close()
    connection.close()
