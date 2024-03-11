import mysql.connector

#Connect to zipcodes_one database
def connect_one(query):
    # Set connection and cursor variables outside the try-block to avoid errors in the finally-block.
    connection = None
    cursor = None
    try:
        # Connect to sharded-service listener
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port='4000',  # Listener is mapped on port 4000
            user='maxuser',
            password='maxpwd',
        )

        # Create cursor to execute the query
        cursor = connection.cursor()

        # Execute USE statement to select the zipcodes_one database
        cursor.execute("USE zipcodes_one")
        
        # Execute the query
        cursor.execute(query)
        # Fetch all rows returned by the query
        rows = cursor.fetchall()

        return rows


    except mysql.connector.Error as e:
        # Print error if an exception occurs
        print("Error:", e)


    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()

# Connect to zipcodes_two database.
def connect_two(query):
    # Set connection and cursor variables outside the try-block to avoid errors in the finally-block.
    connection = None
    cursor = None
    # Connect to sharded-service listener
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port='4000',  # Listener is mapped to port 4000
            user='maxuser',
            password='maxpwd',
        )

        # Create cursor to execute the query
        cursor = connection.cursor()

        # Execute USE statement to select the zipcodes_two database
        cursor.execute("USE zipcodes_two")
        
        # Execute the query
        cursor.execute(query)
        # Fetch all rows returned by the query
        rows = cursor.fetchall()

        return rows


    except mysql.connector.Error as e:
        # Print error if an exception occurs
        print("Error:", e)


    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()

        if connection and connection.is_connected():
            connection.close()


def query_one():
    try:
        # Get the largest zipcode in zipcodes_one
       largest_zip = connect_one("SELECT MAX(zipcode) FROM zipcodes_one;")

       print("The largest zipcode in zipcodes_one is:", largest_zip)

    except Exception as e:
        # Print error if an exception occurs
        print("Error:", e)

def query_two():
    try:
        # All zipcodes where state=KY (Kentucky)
        zipcodes_one = connect_one("SELECT zipcode FROM zipcodes_one WHERE State='KY';")
        zipcodes_two = connect_two("SELECT zipcode FROM zipcodes_two WHERE State='KY';")

        # Combine the results from both databases
        all_zipcodes = zipcodes_one + zipcodes_two

        print("All zipcodes where state=KY (Kentucky):")
        for row in all_zipcodes:
            print(row)

    except Exception as e:
        # Print error if an exception occurs
        print("Error:", e)

def query_three():
    try:
        # All zipcodes between 40000 and 41000
        zipcodes_one = connect_one("SELECT zipcode FROM zipcodes_one WHERE zipcode BETWEEN 40000 AND 41000;")
        zipcodes_two = connect_two("SELECT zipcode FROM zipcodes_two WHERE zipcode BETWEEN 40000 AND 41000;")

        # Combine the results from both databases
        all_zipcodes = zipcodes_one + zipcodes_two

        print("All zipcodes between 40000 and 41000:")
        for row in all_zipcodes:
            print(row)

    except Exception as e:
        # Print error if an exception occurs
        print("Error:", e)

def query_four():
    try:
        # All wages where state is "PA"
        wages = connect_two("SELECT TotalWages FROM zipcodes_two WHERE state='PA';")

        # There are no Pennsylvania zipcodes in zipcodes_two. I put this here just so this query generates some output.
        if wages:
            print("The Total Wages for each zipcode in Pennsylvania are:")
            for row in wages:
                print(row)
        else:
            print("No wages found in zipcodes_two for the state of Pennsylvania.")

    except Exception as e:
        # Print error if an exception occurs
        print("Error:", e)

def main():
    # Execute all queries
    query_one()
    query_two()
    query_three()
    query_four()

if __name__ == "__main__":
    main()
