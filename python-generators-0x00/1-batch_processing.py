#!/usr/bin/python3
import mysql.connector


def stream_users_in_batches(batch_size):
    """
    Generator function that fetches rows from the user_data table in batches.
    Yields:
        list of dict: a batch of user records as dictionaries
    """
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Evan@..6100.",  
        database="ALX_prodev"
    )

    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT user_id, name, email, age FROM user_data")

    while True:
        batch = cursor.fetchmany(batch_size)
        if not batch:
            break
        yield batch  # use yield, not return

    cursor.close()
    connection.close()


def batch_processing(batch_size):
    """
    Processes each batch streamed from the database and filters users over age 25.
    Prints each matching user.
    """
    for batch in stream_users_in_batches(batch_size):
        for user in batch:
            if user["age"] > 25:
                print(user)
