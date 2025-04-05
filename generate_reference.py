import random
import string

#Function to generate a unique booking reference
def generate_booking_reference(cursor):
    while True:
        #Generate a random alphanumeric reference with 8 characters
        booking_reference=''.join(random.choices(string.ascii_uppercase + string.digits,k=8))
        
        #Check if the generated reference already exists in the database
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE reference=?",(booking_reference,))
        
        #If no rows are returned, it means the reference is unique
        if cursor.fetchone()[0]==0:
            break  #Exit the loop if the reference is unique
            
    return booking_reference
