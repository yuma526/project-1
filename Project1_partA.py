import sqlite3 #Import SQLite module to interact with a database
import random
import string

#Seat class:Manages seat information and operations
class Seat:
    def __init__(self, seat_id):
        self.seat_id=seat_id  #Seat ID (e.g.,'1A','2B')
        self.status="F"  #"F"=Free, "R"=Reserved, booking reference if reserved
        self.customer=None  #No customer assigned initially

    def is_free(self):
        return self.status=="F"  #Return True if the seat is free (status "F")
    
    def reserve(self, customer_name, passport_number, booking_reference):
        #Reserve the seat by changing status to the booking reference and storing customer info
        self.status=booking_reference
        self.customer={"name": customer_name, "passport": passport_number, "reference": booking_reference}

    def free(self):
        #Free the seat by resetting status and removing customer info
        self.status="F"
        self.customer=None

#Booking class: Manages the booking information
class Booking:
    def __init__(self, reference, customer_name, passport_number, seat):
        self.reference=reference  #Booking reference (unique identifier)
        self.customer_name=customer_name  #Customer's full name
        self.passport_number=passport_number  #Customer's passport number
        self.seat=seat  #The seat associated with the booking

    def save(self, cursor):
        #Save the booking information into the database
        cursor.execute("INSERT INTO bookings (reference, customer_name, passport_number, seat_id) VALUES (?, ?, ?, ?)",
                       (self.reference, self.customer_name, self.passport_number, self.seat.seat_id))

#Database class: Manages interactions with the SQLite database
class Database:
    def __init__(self, db_name='booking_system.db'):
        self.conn=sqlite3.connect(db_name)  #Connect to the database
        self.cursor=self.conn.cursor()  #Create a cursor to execute SQL queries
        self.create_tables()  #Create tables if they don't exist

    def create_tables(self):
        #Create 'seats' table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS seats (
                                seat_id TEXT PRIMARY KEY,
                                status TEXT,
                                customer_name TEXT)''')
        #Create 'bookings' table if it doesn't exist
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS bookings (
                                reference TEXT PRIMARY KEY, 
                                customer_name TEXT,
                                passport_number TEXT,
                                seat_id TEXT)''')
        self.conn.commit()  #Commit the changes to the database

    def load_seats(self):
        #Load all seats from the database into a dictionary
        self.cursor.execute("SELECT seat_id, status, customer_name FROM seats")
        rows=self.cursor.fetchall()  # Fetch all rows from the seats table
        seats={}  #Dictionary to store Seat objects
        for row in rows:
            seat_id, status, customer_name=row  #Extract seat details from each row
            seat=Seat(seat_id)  #Create a new Seat object for each row
            seat.status=status  #Set the seat's status
            if customer_name:
                seat.customer={"name": customer_name}  #Assign customer information if available
            seats[seat_id]=seat  #Add the seat to the dictionary
        return seats  #Return the dictionary of seats

    def save_seat(self, seat):
        #Save the updated seat information to the database
        self.cursor.execute('''INSERT OR REPLACE INTO seats (seat_id, status, customer_name)
                               VALUES (?, ?, ?)''', 
                               (seat.seat_id, seat.status, seat.customer["name"] if seat.customer else None))
        self.conn.commit()  #Commit the changes to the database

    def close(self):
        #Close the database connection
        self.conn.close()

#ReservationSystem class: Manages the entire reservation system
class ReservationSystem:
    def __init__(self):
        self.database=Database()  #Create a Database object to interact with the database
        self.seats=self.database.load_seats()  #Load all seats into the system

    def generate_booking_reference(self):
        #Generate a unique booking reference
        while True:
            booking_reference=''.join(random.choices(string.ascii_uppercase + string.digits, k=8))  #Random 8-character reference
            self.database.cursor.execute("SELECT COUNT(*) FROM bookings WHERE reference=?",(booking_reference,))
            if self.database.cursor.fetchone()[0]==0:  #Check if the reference is unique
                return booking_reference  #Return the unique booking reference

    def book_seat(self, seat_id,customer_name,passport_number):
        #Book a seat if it's available
        seat=self.seats.get(seat_id)  #Get the Seat object based on seat_id
        if seat and seat.is_free():  #If the seat exists and is free
            booking_reference=self.generate_booking_reference()  #Generate a unique booking reference
            seat.reserve(customer_name, passport_number, booking_reference)  #Reserve the seat
            booking=Booking(booking_reference, customer_name, passport_number, seat)  #Create a Booking object
            booking.save(self.database.cursor)  #Save the booking to the database
            self.database.save_seat(seat)  #Save the seat's updated status to the database
            print(f"Seat {seat_id} has been successfully booked for {customer_name}.")
        else:
            print(f"Seat {seat_id} is not available or invalid.")  #If the seat is not available or invalid

    def free_seat(self, seat_id):
        #Free a reserved seat
        seat=self.seats.get(seat_id)  #Get the Seat object based on seat_id
        if seat and not seat.is_free():  #If the seat is reserved
            seat.free()  #Free the seat
            self.database.save_seat(seat)  # ave the seat's updated status to the database
            print(f"Seat {seat_id} has been freed.")
        else:
            print(f"Seat {seat_id} is already free or invalid.")  #If the seat is already free or invalid

    def show_booking_status(self, customer_name):
        #Show the booking status for a customer by name
        found=False
        for seat in self.seats.values():  #Iterate through all the seats
            if seat.customer and seat.customer["name"].lower()==customer_name.lower():  #Check if the customer matches
                found=True
                print(f"Seat {seat.seat_id}: Booked by {seat.customer['name']}")  #Display the booking details
        if not found:
            print(f"No booking found for {customer_name}.")  #If no booking found for the customer

    def check_availability(self):
        #Display available seats
        print("\nAvailable Seats:")
        for row in ['A', 'B', 'C', 'D', 'E', 'F']:  #Loop through rows A-F
            available_seats=[f"{col}{row}" for col in range(1, 81) if self.seats[f"{col}{row}"].is_free()]  # Check available seats
            print(f"{row}: {' '.join(available_seats)}")  #Print available seats for the row

    def save_changes(self):
        #Close the database connection and save changes
        self.database.close()

#Main execution
if __name__ == "__main__":
    system = ReservationSystem()  #Create a ReservationSystem object

    #Interactive menu loop
    while True:
        print("\nMenu:")
        print("1. Check availability of seat")
        print("2. Book a seat")
        print("3. Free a seat")
        print("4. Show booking status")
        print("5. Exit")
        choice = input("Enter choice: ")
        
        if choice=='1':
            system.check_availability() #Option to check seat availability
        elif choice=='2':
            seat_id=input("Enter seat ID to book: ") #Input for seat ID
            customer_name=input("Enter name:") #Input for customer name
            passport_number=input("Enter passport number: ") #Input for passport number
            system.book_seat(seat_id, customer_name, passport_number) #Book the seat
        elif choice=='3':
            seat_id=input("Enter seat ID to free: ") #Input for seat ID
            system.free_seat(seat_id) #Free the seat
        elif choice=='4':
            customer_name=input("Enter customer name to check status: ") #Input for customer name 
            system.show_booking_status(customer_name) #Show booking status for customer
        elif choice=='5':
            system.save_changes() #Save changes and close the program
            print("Exiting...")
            break #Exit the program
        else:
            print("Invalid choice. Please try again.") #Handle invalid choices

