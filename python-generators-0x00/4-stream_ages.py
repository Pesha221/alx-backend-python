#!/usr/bin/python3
"""
Memory-Efficient Average Age Calculator using Generators
"""
seed = __import__('seed')


def stream_user_ages():
    """
    Generator that streams user ages one by one from the user_data table.
    """
    connection = seed.connect_to_prodev()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT age FROM user_data")

    for row in cursor:
        yield row['age']

    cursor.close()
    connection.close()


def compute_average_age():
    """
    Compute the average age of users without loading the full dataset into memory.
    Uses only two loops maximum.
    """
    total = 0
    count = 0

    for age in stream_user_ages():
        total += age
        count += 1

    if count > 0:
        avg = total / count
        print(f"Average age of users: {avg:.2f}")
    else:
        print("No user data found.")


if __name__ == "__main__":
    compute_average_age()
