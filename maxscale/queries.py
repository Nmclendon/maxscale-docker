import mysql.connector

def connect_one(query):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port='4000',  # master1 is mapped on port 4002
            user='maxuser',
            password='maxpwd',
            database='zipcodes_one'
        )

        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return rows

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def connect_two(query):
    connection = None
    cursor = None
    try:
        connection = mysql.connector.connect(
            host='127.0.0.1',
            port='4000',  # master2 is mapped to port 4003
            user='maxuser',
            password='maxpwd',
            database='zipcodes_two'
        )

        cursor = connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()

        return rows

    except mysql.connector.Error as error:
        print("Error:", error)

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def query_one():
    try:
       largest_zip = connect_one("SELECT MAX(zipcode) FROM zipcodes_one;")
       print("The largest zipcode in zipcodes_one is:", largest_zip)

    except Exception as e:
        print("Error:", e)

def query_two():
    try:
        # All zipcodes where state=KY (Kentucky)
        zipcodes_one = connect_one("SELECT zipcode FROM zipcodes_one WHERE State='KY';")
        zipcodes_two = connect_two("SELECT zipcode FROM zipcodes_two WHERE State='KY';")

        # Combine the results from both databases
        all_zipcodes = zipcodes_one + zipcodes_two

        # Print the combined results
        print("All zipcodes where state=KY (Kentucky):")
        for row in all_zipcodes:
            print(row)

    except Exception as e:
        print("Error:", e)

def query_three():
    try:
        # All zipcodes between 40000 and 41000
        zipcodes_one = connect_one("SELECT zipcode FROM zipcodes_one WHERE zipcode BETWEEN 40000 AND 41000;")
        zipcodes_two = connect_two("SELECT zipcode FROM zipcodes_two WHERE zipcode BETWEEN 40000 AND 41000;")

        all_zipcodes = zipcodes_one + zipcodes_two

        print("All zipcodes between 40000 and 41000:")
        for row in all_zipcodes:
            print(row)

    except Exception as e:
        print("Error:", e)

def query_four():
    try:
        # All wages where state is "PA"
        wages = connect_two("SELECT TotalWages FROM zipcodes_two WHERE state='PA';")

        print("The Total Wages for each zipcode in Pennsylvania are:")
        for row in wages:
            print(row)

    except Exception as e:
        print("Error:", e)

def main():
    query_one()
    query_two()
    query_three()
    query_four()

if __name__ == "__main__":
    main()