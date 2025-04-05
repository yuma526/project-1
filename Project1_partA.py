import sqlite3  #Import SQLite module to interact with a database

#Initialize seating with 6 rows (A-F) and 80 columns (1-80)
def initialize_seats():
    rows=['A', 'B', 'C', 'D', 'E', 'F']   #Define row labels A to F
    columns=range(1, 81)  #Define column numbers 1 to 80
    #Return a dictionary where each key is the seat ID (e.g., "1A"), and the value is a dictionary with status and customer info
    return {f"{col}{row}": {"status": "F", "customer": None} for row in rows for col in columns}

#Database connection setup
def create_db():
    conn=sqlite3.connect('booking_system.db')  #Create (or connect to) an SQLite database file
    cursor=conn.cursor()  #Create a cursor object to execute SQL queries
    #Create the 'seats' table if it doesn't already exist
    cursor.execute('''CREATE TABLE IF NOT EXISTS seats (
                        seat_id TEXT PRIMARY KEY,
                        status TEXT,
                        customer_name TEXT)''')
    conn.commit()  #Commit the changes to the database
    return conn, cursor  # Return the connection and cursor for use in other functions

#Load seats data from the database
def load_seats_from_db(cursor):
    #Execute a query to retrieve all seat data from the 'seats' table
    cursor.execute("SELECT seat_id, status, customer_name FROM seats")
    rows=cursor.fetchall()  #Fetch all results from the query
    seats=initialize_seats()  #Initialize default seats in case the database is empty

    #Loop through the rows and update the 'seats' dictionary with the data from the database
    for row in rows:
        seat_id, status, customer_name = row  #Unpack each row into seat_id, status, and customer_name
        #If the seat has a customer name, store it in the dictionary
        seats[seat_id]={"status": status, "customer": {"name": customer_name} if customer_name else None}
    
    return seats  #Return the updated seats dictionary

#Save seat data to the database
def save_seats_to_db(conn, cursor, seats):
    #Loop through each seat in the 'seats' dictionary
    for seat_id, seat_info in seats.items():
        # Insert or update the seat information in the database
        cursor.execute('''INSERT OR REPLACE INTO seats (seat_id, status, customer_name)
                          VALUES (?, ?, ?)''', 
                       (seat_id, seat_info["status"], seat_info["customer"]["name"] if seat_info["customer"] else None))
    conn.commit()  #Commit the changes to the database to save them

#Function to display the seat availability in a table format
def check_availability(seats):
    print("\nAvailable Seats:")
    #Print column numbers for easier reference (1 to 80)
    print("Row " + " ".join([str(i) for i in range(1, 81)]))
    #Loop through each row (A to F)
    for row in ['A', 'B', 'C', 'D', 'E', 'F']:
        #For each row, loop through columns (1 to 80) and check if the seat is free (status = "F")
        row_display = [f"{col}{row}" if seats[f"{col}{row}"]['status']=="F" else "  " for col in range(1, 81)]
        #Print the row and the availability of each seat in that row
        print(f"{row}  " + " ".join(row_display))
    print("\n")


#Function to book one or more seats
def book_seat(seats):
    #Prompt the user to enter seat(s) to book, split input by commas
    seats_to_book=input("Enter seat(s) to book (e.g., 1A, 2B, 3C): ").split(',')
    booked_seats=[]  #Initialize a list to keep track of successfully booked seats
    
    #Loop through each seat entered by the user
    for seat in seats_to_book:
        seat = seat.strip().upper()  # Remove leading/trailing spaces and convert to uppercase
        if seat in seats:  # Check if the seat exists in the dictionary
            if seats[seat]["status"] == "F":  # Check if the seat is free
                print(f"Selected Seat: {seat}")
                # Ask for the customer's name
                customer_name = input("Enter customer name: ")
                # Update the seat status to 'R' for reserved, and store the customer information
                seats[seat]["status"] = "R"
                seats[seat]["customer"] = {"name": customer_name}
                booked_seats.append(seat)  # Add the booked seat to the list
                print(f"Seat {seat} has been successfully booked for {customer_name}.")
            else:
                print(f"Seat {seat} is already booked.")  # Inform the user if the seat is already reserved
        else:
            print(f"Invalid seat {seat}.")  # Inform the user if the seat is not valid
    
    #If there are booked seats, display a success message
    if booked_seats:
        print(f"Seats {', '.join(booked_seats)} have been successfully booked.")
    else:
        print("No valid seats were booked.")

#Function to free a seat
def free_seat(seats):
    #Prompt the user to enter the seat they want to free
    seat_to_free=input("Enter seat to free (e.g., 1A, 2B, 3C): ").strip().upper()
    if seat_to_free in seats:  #Check if the seat exists in the dictionary
        if seats[seat_to_free]["status"]=="R":  #Check if the seat is reserved
            #Update the seat status to 'F' for free and remove the customer information
            seats[seat_to_free]["status"]="F"
            seats[seat_to_free]["customer"]=None
            print(f"Seat {seat_to_free} has been freed.")
        else:
            print(f"Seat {seat_to_free} is not currently booked.")  #Inform the user if the seat is not reserved
    else:
        print(f"Invalid seat {seat_to_free}.")  #Inform the user if the seat is not valid

#Function to show booking status for a specific customer
def show_booking_status(seats):
    #Prompt the user to enter the customer's name
    customer_name=input("Enter customer name to check booking status: ").strip()
    found=False  #Flag to track if any booking was found for the customer
    #Loop through each seat in the seats dictionary
    for seat_id, seat_info in seats.items():
        #If the seat is reserved and the customer's name matches, display the booking details
        if seat_info["status"]=="R" and seat_info["customer"] and seat_info["customer"]["name"].lower()==customer_name.lower():
            found=True
            print(f"Seat {seat_id}: Booked by {seat_info['customer']['name']}")
    
    #If no booking was found, inform the user
    if not found:
        print(f"No booking found for {customer_name}.")
    print("\n")

#Main menu to interact with the user
def main_menu():
    conn, cursor = create_db()  # Create database connection and cursor
    seats = load_seats_from_db(cursor)  # Load seat data from the database

    while True:
        # Display menu options to the user
        print("Menu:")
        print("1. Check availability of seat")
        print("2. Book seat(s)")
        print("3. Free a seat")
        print("4. Show booking status")
        print("5. Exit program")
        choice = input("Select an option: ")

        # Handle user choice
        if choice == "1":
            check_availability(seats)  # Check seat availability
        elif choice == "2":
            book_seat(seats)  # Book one or more seats
        elif choice == "3":
            free_seat(seats)  # Free a reserved seat
        elif choice == "4":
            show_booking_status(seats)  # Show booking status for a specific customer
        elif choice == "5":
            save_seats_to_db(conn, cursor, seats)  # Save updated seat data to the database before exiting
            print("Exiting program.")
            break  # Exit the loop and terminate the program
        else:
            print("Invalid option, please choose again.")  # Handle invalid menu options

if __name__ == "__main__":
    main_menu()  #Start the program