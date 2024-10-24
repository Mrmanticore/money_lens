import sqlite3
import csv

def export_to_csv(db_file):
    try:
        # Connect to the SQLite database file
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # List all tables in the database
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if tables:
            print("Tables found in the database:", tables)

            # Export each table to a separate CSV file
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT * FROM {table_name}")

                # Fetch column names for the CSV header
                column_names = [description[0] for description in cursor.description]

                # Fetch all rows from the table
                rows = cursor.fetchall()

                # Write to CSV file
                csv_filename = f"{table_name}.csv"
                with open(csv_filename, mode='w', newline='') as csv_file:
                    writer = csv.writer(csv_file)
                    
                    # Write the header
                    writer.writerow(column_names)
                    
                    # Write the data rows
                    writer.writerows(rows)

                print(f"Table '{table_name}' exported to {csv_filename}")

        else:
            print("No tables found in the database.")
    
    except sqlite3.Error as e:
        print("An error occurred:", e)
    
    finally:
        # Close the connection when done
        if conn:
            conn.close()

# Export the SQLite database to CSV
export_to_csv('contact.db')
