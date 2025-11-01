#!/usr/bin/python3
import mysql.connector

def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows from the user_data table in batches.
    Yields:
        list of dict: A batch (list) of user records as dictionaries
    """
    # Connect to database
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Evan@..6100.",  
        database="ALX_prodev"
    )

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, age FROM user_data")

    # Fetch data in batches
    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch  # yield one batch at a time

    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """
    Processes each batch from the stream_users_in_batches generator
    Filters and prints users over the age of 25
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user["age"] > 25:
                print(user)
