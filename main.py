from datetime import datetime
from invoices import generate_invoice
from database1 import get_invoice_data
from database1 import (
    create_tables,insert_valid_rooms,find_guest_by_mobile,allocate_room,
    get_completed_stays,get_all_rooms,search_availability,get_room_details,
    insert_booking,get_book_details,update_booking_status,
    get_occupancy_report,get_revenue,get_guest_stay_history,cancel_booking_record,create_connection
    )
from guest_services import guestservices,get_guest_details
from room_csv_validation import rooms
from pricing import Pricing
from models import Guest
def convert_date(date):
    return datetime.strptime(date,"%d-%m-%Y").strftime("%Y-%m-%d")

def search_room_availability():
    try:
        room_type=input("Enter Room Type :").strip().capitalize()
        check_in=input("Enter check-in date:")
        check_out=input("Enter check_out date:")
        no_of_guests=int(input("Enter number of guests:"))
        check_in_db=convert_date(check_in)
        check_out_db=convert_date(check_out)
        if datetime.strptime(check_out_db,"%Y-%m-%d")<=datetime.strptime(check_in_db,"%Y-%m-%d"):
            print("Check-out date must be after check-in date")
            return
        
        result=search_availability(room_type,check_in_db,check_out_db,no_of_guests)
        if not result:
            print(f"No {room_type} rooms available for {no_of_guests} guests.")
            print("\nChecking other room types")
            other_rooms=get_all_rooms()
            available_rooms=[]
            for room in other_rooms:
                if room[1]!=room_type and room[4]>=no_of_guests:
                    available_rooms.append(room)
            if not available_rooms:
                print("No other room types can accommodate the guests.")
                return
            print("\nOther available rooms:")
            for room in available_rooms:
                print("Room Number:",room[0],"Room Type:",room[1],
                    "Floor:",room[2],"Rate:",room[3],
                    "Maximum Guests:",room[4])
            return
        print("\nAvailable Rooms")
        for room in result:
            print("Room Number:",room[0],"Room Type:",room[1],
                "Floor:",room[2],"Rate:",room[3],"Maximum Guests:",room[4])
    except (ValueError,TypeError) as e:
        print("Error:",e)
def create_booking():
    while True:
        try:
            mobile=input("Enter mobile number:")
            existing_guest=find_guest_by_mobile(mobile)
            
            if existing_guest:
                print("Registered guest found")
                print("Guest Name:",existing_guest[2])
                no_of_guests=input("Enter number of guests: ")
                guest=Guest(existing_guest[2],existing_guest[1],existing_guest[3],no_of_guests)
                guest_id=guestservices().register_guest(guest)
            else:
                print("Guest not registered")
                while True:
                    try:
                        name=input("Guest Name:")
                        email=input("Email:")
                        no_of_guests=input("Number of Guests:")
                        guest=Guest(name,mobile,email,no_of_guests)
                        break
                    except ValueError as e:
                        print("Error:",e)
                        
                guest_id=guestservices().register_guest(guest)
            room_type=input("Enter Room Type (Standard/Deluxe/Suite):").strip().capitalize()
            check_in=input("Enter Check-in Date (DD-MM-YYYY):")
            check_out=input("Enter Check-out Date (DD-MM-YYYY):")
            check_in_db=convert_date(check_in)
            check_out_db=convert_date(check_out)
            if check_out_db<=check_in_db:
                print("Check-out date must be after check-in date")
                return
            no_of_guests=guest.get_noofguests()
            selected_room=allocate_room(room_type,no_of_guests,check_in_db,check_out_db,rooms)
            if selected_room is None:
                return
            breakfast=input("Do you want break fast:").strip().lower()
            if breakfast not in ["yes","no"]:
                print("Please enter yes or no")
                return 
            
            completed_stays = get_completed_stays(guest_id)
            pricing = Pricing()
            amount = pricing.calculate_room_charges(
                selected_room.room_type, selected_room.get_base_rate(),
                check_in_db, check_out_db, no_of_guests, completed_stays, breakfast
            )
            
            booking_id=insert_booking(
                guest_id,selected_room.room_no,check_in_db,check_out_db,
                no_of_guests,amount["room_revenue"],
                amount["gst_amount"],"CONFIRMED"
            )  
            print("\nBooking Confirmed")
            print("Booking ID:",booking_id)
            print("Room Number:",selected_room.room_no)
            print("Number of Nights:",amount["no_of_nights"])
            print("Room Charge:",round(amount["room_charge"],2))
            print("Extra Guest Charge:",round(amount["extra_guest_charge"],2))
            print("Breakfast Charge:",round(amount["breakfast_charge"],2))
            print("Discount:",round(amount["total_discount"],2))
            print("GST:",round(amount["gst_amount"],2))
            print("Final Amount:",round(amount["final_amount"],2))
        except Exception as e:
            print("Unable to create:",e)
        break
def check_in():
    try:
        booking_id=int(input("Enter booking_id:"))
        booking=get_book_details(booking_id)
        if booking is None:
            print("Booking not found")
            return
        if booking[7]=="CHECKED_OUT":
            print("Guest has already checked out")
            return
        if booking[7]=="CHECKED_IN":
            print("Guest is already checked in")
            return
        if booking[7]=="CANCELLED":
            print("Cancelled booking cannot be checked in")
            return
        if booking[7]=="CONFIRMED":
            update_booking_status(booking_id,"CHECKED_IN")
            print("Guest checked in successfully")
    except ValueError:
        print("Enter valid booking ID")

def check_out():
    try:
        booking_id=int(input("Enter Booking ID:"))
        booking=get_book_details(booking_id)
        if booking is None:
            print("Booking not found")
            return
        filename=f"invoices/BK{booking_id:04d}.txt"
        if booking[7]=="CHECKED_OUT":
            try:
                with open(filename,"r"):
                    print("Invoice already exists:",filename)
            except FileNotFoundError:
                invoice_data=get_invoice_data(booking_id)
                if invoice_data is not None:
                    generate_invoice(invoice_data)
                    print("Invoice created:",filename)
            return
        if booking[7]=="CANCELLED":
            print("Cancelled booking cannot be checked out")
            return
        if booking[7]=="CONFIRMED":
            print("Guest has not checked in yet")
            return
        if booking[7]!="CHECKED_IN":
            print("Invalid booking status")
            return
        check_in_date=datetime.strptime(
            booking[3],"%Y-%m-%d").date()
        actual_checkout_date=datetime.today().date()
        if actual_checkout_date<=check_in_date:
            print("Invalid checkout date. Guest must stay at least one night.")
            return
        actual_nights=(actual_checkout_date-check_in_date).days
        print("Original checkout date:",booking[4])
        print("Actual checkout date:",actual_checkout_date)
        print("Actual nights stayed:",actual_nights)
        invoice_data=get_invoice_data(booking_id)
        if invoice_data is None:
            print("Invoice details not found")
            return
        invoice_data=list(invoice_data)
        invoice_data[7]=actual_checkout_date.strftime("%Y-%m-%d")
        generate_invoice(tuple(invoice_data))
        conn=create_connection()
        cur=conn.cursor()
        cur.execute("""
            UPDATE bookings
            SET booking_status='CHECKED_OUT',
                check_out=?
            WHERE booking_id=?
        """,(invoice_data[7],booking_id))

        conn.commit()
        conn.close()

        print("\nCheckout completed successfully")
        print("Booking Status: CHECKED_OUT")
        print("Invoice saved at:",filename)

    except Exception as e:
        print("Checkout Error:",e)


def cancel_booking():
    try:
        booking_id=int(input("Enter booking id:"))
        booking=get_book_details(booking_id)
        if booking is None:
            print("Booking not found")
            return 
        if booking[7]!="CONFIRMED":
            print("Only confirmed booking can be cancelled")
            return
        check_in=datetime.strptime(booking[3],"%Y-%m-%d").date()
        today=datetime.today().date()
        days_before_checkin=(check_in-today).days
        total_amount=booking[6]
        if days_before_checkin>=7:
            refund_amount=total_amount
            print("Refuned 100%")
        elif days_before_checkin>=2:
            refund_amount=total_amount*0.50
            print("refunded 50%")
        else:
            refund_amount=0
            print("Refunded 0%")
        cancel_booking_record(booking_id)
        # update_booking_status(booking_id,"CANCELLED")
        print('Booking cancelled')
        print("Booking ID:",booking_id)
        print("Total_Amount:",total_amount)
        print("Refund Amount:",refund_amount)
    except ValueError:
        print("Enter a valid booking id")
def view_booking_details():
    try:
        # update_booking_status()
        booking_id=int(input("Enter booking id:"))
        booking=get_book_details(booking_id)
        if booking is None:
            print("Booking not found")
            return 
        print("\nBooking Details")
        print("Booking ID:",booking[0])
        print("Guest ID:",booking[1])
        print("Room Number:",booking[2])
        print("Check-in:",booking[3])
        print("Check-out:",booking[4])
        print("Number of Guests:",booking[5])
        print("Total Amount:",booking[6])
        print("Booking Status:",booking[7])
        print("Room Type:",booking[8])
        print("Guest Name:",booking[10])
        print("Mobile Number:",booking[11])
    except ValueError:
        print("Enter valid booking Id")

def guest_stay_history():
    try:
        mobile=input("Enter mobile number:")
        guest=find_guest_by_mobile(mobile)
        if guest is None:
            print("No guest found")
            return
        history=get_guest_stay_history(guest[0])
        if not history:
            print("No stay history found")
            return
        print("\nGuest Stay History")
        for row in history:
            print(row)
    except Exception as e:
        print('Error:',e)

def occupancy_report():
    result=get_occupancy_report()
    print("\nOccupancy Report")
    if not result:
        print("No occupancy data available")
        return
    for row in result:
        print("Room Number:",row[0],"Room Type:",row[1],"Bookings:",row[2])
def revenue_report():
    result=get_revenue()
    print("\nRevenue Report")
    print("Completed Bookings:",result[0])
    print("Total Revenue:",round(result[1],2))

def revenue_report():
    result=get_revenue()
    print("\n===REVENUE REPORT===")
    if not result:
        print("No room records found")
        return
    for row in result:
        print("\nRoom Type:",row[0])
        print("Completed Stays:",row[1])
        print("Room Revenue:",round(row[2],2))
        print("GST Collected:",round(row[3],2))
        print("Cancellation Amount Kept:",round(row[4],2))
        
  
def create_invoice():
    try:
        booking_id=int(input("Enter Booking ID:"))
        booking=get_book_details(booking_id)
        if booking is None:
            print("Booking not found")
            return
        invoice_data=get_invoice_data(booking_id)
        if invoice_data is None:
            print("Invoice details not found")
            return
        filename=f"invoices/BK{booking_id:04d}.txt"
        try:
            with open(filename,"r"):
                print("Invoice already exists:",filename)
                return
        except FileNotFoundError:
            pass
        generate_invoice(invoice_data)
        print("Invoice generated successfully")
        print("Invoice saved at:",filename)
    except Exception as e:
        print("Invoice Error:",e)
        
def export_bookings_to_csv():
    import csv
    import os
    from database1 import get_bookings
    bookings=get_bookings()
    with open("bookings_export.csv","w",newline="",encoding="utf-8") as file:
        writer=csv.writer(file)
        writer.writerow(["Booking ID","Guest ID","Room Number","Check-in",
                        "Check-out","Guests","Total Amount","Status"])
        writer.writerows(bookings)
    print("Bookings exported to bookings_export.csv")

def main():
    create_tables()
    inserted=insert_valid_rooms(rooms)
    print("Inserted rooms:",inserted)
    
    while True:
        print("\n=====Hotel Booking=====")
        print("1. Search Room Availability")
        print("2. Create Booking")
        print("3. Check In")
        print("4. Check Out")
        print("5. Cancel Booking")
        print("6. View Booking Details")
        print("7. Guest Stay History")
        print("8. Occupancy Report")
        print("9. Revenue Report")
        print("10. Export all bookings to CSV")
        print("11.Invoice generation")
        print("12. Exit")

        choice=input("Enter your choice:")
        if choice=="1":
            search_room_availability()
        elif choice=="2":
            create_booking()
        elif choice=="3":
            check_in()
        elif choice=="4":
            check_out()
        elif choice=="5":
            cancel_booking()
        elif choice=="6":
            view_booking_details()
        elif choice=="7":
            guest_stay_history()
        elif choice=="8":
            occupancy_report()
        elif choice=="9":
            revenue_report()
        elif choice=="10":
            export_bookings_to_csv()
        elif choice=="11":
            create_invoice()
        elif choice=="12":
            print("Exitinggg")
            break
        else:
            print("Invalid choice.Please select from 1 to 11.")
main()