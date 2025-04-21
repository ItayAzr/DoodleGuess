import sqlite3


def delete():
    # Connect to the database
    connection = sqlite3.connect('DataBase.db')

    # Create a cursor object to execute SQL commands
    cursor = connection.cursor()

    # Define a SQL query to create a table
    delete = '''
        DROP TABLE users;
       '''

    # Execute the query
    cursor.execute(delete)

    print("Table created successfully!")

    # Commit changes and close the connection
    connection.commit()
    connection.close()


def create_db():
    # Connect to the database
    connection = sqlite3.connect('DataBase.db')

    # Create a cursor object to execute SQL commands
    cursor = connection.cursor()

    # Define a SQL query to create a table
    create_table_query = '''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        wins INTEGER NOT NULL DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    '''

    # Execute the query
    cursor.execute(create_table_query)

    print("Table created successfully!")

    # Commit changes and close the connection
    connection.commit()
    connection.close()

delete()
create_db()