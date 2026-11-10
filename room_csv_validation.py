import csv
from exceptions import Easystay, RoomUnavailable
from abc import ABC,abstractmethod
from models import Guest,StandardRoom,DeluxeRoom,SuiteRoom,Booking
from guest_services import guestservices,get_guest_details

room_data=[]
valid_rooms=[]
rooms=[]
seen=set()
with open(r"C:\Users\varshini.anumalla\OneDrive - Acuvate Software Private Limited\Desktop\booking_project_modifications\mini_project_hotel_reservation\rooms.csv","r") as room_file:
    reader=csv.DictReader(room_file)
    for row in reader:
        room_data.append(row)
with open(r"C:\Users\varshini.anumalla\OneDrive - Acuvate Software Private Limited\Desktop\booking_project_modifications\mini_project_hotel_reservation\errors.log","w") as log_file:
    for row in room_data:
        try:
            valid=True
            if row["room_no"]=="" or row["room_no"] in seen:
                raise RoomUnavailable("Room number cannot be empty or duplicate")
            if row["room_type"].capitalize() not in ["Standard","Deluxe","Suite"]:
                raise RoomUnavailable("Room type should be Standard, Deluxe or Suite")
            if int(row["floor"])<0:
                raise RoomUnavailable("Floor number cannot be negative")
            seen.add(row["room_no"])
            if valid:
                valid_rooms.append(row)
        except Easystay as e:
            log_file.write(f"Error:{e} Room data:{row}\n")
        except ValueError as e:
            log_file.write(f"Invalid floor value:{e}|Room data:{row}\n")
# print(valid_rooms)
for row in valid_rooms:
    if row["room_type"].capitalize()=="Standard":
        room=StandardRoom(int(row["room_no"]),row["room_type"],int(row["floor"]))
    elif row["room_type"].capitalize()=="Deluxe":
        room=DeluxeRoom(int(row["room_no"]),row["room_type"],int(row["floor"]))
    elif row["room_type"].capitalize()=="Suite":
        room=SuiteRoom(int(row["room_no"]),row["room_type"],int(row["floor"]))
    rooms.append(room)
    