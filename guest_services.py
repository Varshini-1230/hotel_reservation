import sqlite3
from models import Guest
from database1 import create_connection
class guestservices:
    def register_guest(self,guest):
        connection=create_connection()
        cursor=connection.cursor()
        cursor.execute("SELECT guest_id FROM guests WHERE mobile_no=?",
                       (guest.get_mobile(),))
        result=cursor.fetchone()
        if result:
            guest_id=result[0]
            cursor.execute("""UPDATE guests
                SET registration_count=registration_count+1 WHERE mobile_no=?""",
                (guest.get_mobile(),))
            connection.commit()
            print("Guest is already registered")
            print("Registration count incremented")
            connection.close()
            return guest_id
        else:
            cursor.execute("""INSERT INTO guests(
                mobile_no,name,email,no_of_guest)
                VALUES(?,?,?,?)""",
                (guest.get_mobile(),guest.get_name(),
                 guest.get_email(),guest.get_noofguests()))
            guest_id=cursor.lastrowid
            connection.commit()
            connection.close()
            print("Guest registered successfully!")
            return guest_id
def get_guest_details():
    while True:
        try:
            name=input("Guest Name:")
            mobile=input("Mobile Number:")
            email=input("Email:")
            no_of_guests=input("Number of Guests:")
            guest=Guest(name,mobile,email,no_of_guests)
            print(guest)
            return guest
        except ValueError as e:
            print("Error:", e)
            print("Please enter all details again.\n")

# service = guestservices()
# guest = get_guest_details()
# result = service.register_guest(guest)
# print("Guest ID:", result)

