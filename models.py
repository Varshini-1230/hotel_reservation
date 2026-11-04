from exceptions import Easystay, RoomUnavailable
from abc import ABC,abstractmethod
from room_csv_validation import valid_rooms
rooms=[]
class Room(ABC):
    def __init__(self,room_no,room_type,floor):
        self.room_no=room_no
        self.room_type=room_type
        self.floor=floor

    @abstractmethod
    def get_base_rate(self):
        pass
    @abstractmethod
    def get_max_guests(self):
        pass
    @abstractmethod
    def get_extra_guest_charge(self,guests):
        pass
    @abstractmethod
    def get_breakfast_charge(self,guests,bresk_fast):
        pass
class StandardRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
    def get_base_rate(self):
        return 2500
    def get_max_guests(self):
        return 2
    def get_extra_guest_charge(self,guests):
        return 0
    def get_breakfast_charge(self, guests,break_fast):
        if break_fast=="yes":
            return 350*guests
        return 0
class DeluxeRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
    def get_base_rate(self):
        return 4000
    def get_max_guests(self):
        return 3
    def get_extra_guest_charge(self,guests):
        return max(0,guests-2)*800
    def get_breakfast_charge(self, guests):
        return 0    
class SuiteRoom(Room):
    def __init__(self, room_no, room_type, floor):
        super().__init__(room_no, room_type, floor)
    def get_base_rate(self):
        return 7500
    def get_max_guests(self):
        return 4
    def get_extra_guest_charge(self,guests):
        return max(0,guests-2)*800
    def get_breakfast_charge(self, guests):
        return 0
# rooms=[]
for row in valid_rooms:
    if row["room_type"].capitalize()=="Standard":
        room=StandardRoom(int(row["room_no"]),row["room_type"],int(row["floor"]))
    elif row["room_type"].capitalize()=="Deluxe":
        room=DeluxeRoom(int(row["room_no"]),row["room_type"],int(row["floor"]))
    elif row["room_type"].capitalize()=="Suite":
        room=SuiteRoom(int(row["room_no"]),row["room_type"],int(row["floor"]))
    rooms.append(room)
# print(len(rooms))
for row in rooms:
    print("\nRoom number:",row.room_no)
    print("Room type:",row.room_type)
    print("Floor:",row.floor)
    print("Base rate:",row.get_base_rate())
    print("Max guest:",row.get_max_guests())
    # print("Extra charge:",row.get_extra_guest_charge())
    # print("Breakfast charge:",row.get_breakfast_charge())

class Guest:
    def __init__(self, name, mobile_no, email, no_of_guests):
        self.set_name(name)
        self.set_mobile(mobile_no)
        self.set_email(email)
        self.set_guests(no_of_guests)
    def set_name(self, name):
        if name.strip() == "":
            raise ValueError("Name cannot be emptyy")
        self.__name = name.strip()
    def get_name(self):
        return self.__name
    def set_mobile(self, mobile_no):
        mobile_no = mobile_no.strip()
        if len(mobile_no) != 10 or not mobile_no.isdigit() or int(mobile_no[0]) not in [6,7,8,9]:
            raise ValueError("Invalid mobile number")
        self.__mobile_no = mobile_no
    def get_mobile(self):
        return self.__mobile_no
    def set_email(self, email):
        email = email.strip()
        if "@" not in email or "." not in email:
            raise ValueError("Invalid email address")
        self.__email = email
    def get_email(self):
        return self.__email
    def set_guests(self, no_of_guests):
        no_of_guests = int(no_of_guests)
        if no_of_guests < 1:
            raise ValueError("invalid guest number")
        self.__no_of_guests = no_of_guests
    def get_guests(self):
        return self.__no_of_guests
# name=Guest.name="varshini"
# print(name)
    def __str__(self):
        return (f"\nGuest Name:{self.__name}\nMobile Number:{self.__mobile_no}\nEmail:{self.__email}\nNumber of Guests:{self.__no_of_guests}")
guest=Guest("Varshini","9876543210","varshini@gmail.com",3)
print(guest)

