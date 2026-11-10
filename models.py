from exceptions import Easystay, RoomUnavailable,BookingNotFound,InvalidDate,InvalidStatus
from abc import ABC,abstractmethod
from datetime import datetime,timedelta,date
class Room(ABC):
    def __init__(self,room_no,room_type,floor):
        self.room_no=int(room_no)
        self.room_type=room_type.strip().capitalize()
        self.floor=int(floor)

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
    def get_base_rate(self):
        return 4000
    def get_max_guests(self):
        return 3
    def get_extra_guest_charge(self,guests):
        return max(0,guests-2)*800
    def get_breakfast_charge(self, guests,break_fast):
        if break_fast=='yes':
            return 350*guests
        return 0    
class SuiteRoom(Room):
    def get_base_rate(self):
        return 7500
    def get_max_guests(self):
        return 4
    def get_extra_guest_charge(self,guests):
        return max(0,guests-2)*800
    def get_breakfast_charge(self, guests,break_fast):
        if break_fast=="yes":
            return 350*guests
        return 0

class Guest:
    def __init__(self, name,mobile_no,email,no_of_guests):
        self.set_name(name)
        self.set_mobile(mobile_no)
        self.set_email(email)
        self.set_noofguests(no_of_guests)
    def set_name(self, name):
        if name.strip()=="":
            raise ValueError("Name cannot be emptyy")
        self.__name = name.strip()
    def get_name(self):
        return self.__name
    
    def set_mobile(self,mobile_no):
        mobile_no=mobile_no.strip()
        if len(mobile_no)!=10 or not mobile_no.isdigit() or mobile_no[0] not in "6789":
            raise ValueError("Invalid mobile number")
        self.__mobile_no=mobile_no
    def get_mobile(self):
        return self.__mobile_no
    
    def set_email(self, email):
        email = email.strip()
        if "@" not in email or "." not in email:
            raise ValueError("Invalid email address")
        self.__email = email
    def get_email(self):
        return self.__email
    def set_noofguests(self, no_of_guests):
        no_of_guests = int(no_of_guests)
        if no_of_guests < 1:
            raise ValueError("invalid guest number")
        self.__no_of_guests = no_of_guests
    def get_noofguests(self):
        return self.__no_of_guests
# name=Guest.name="varshini"
# print(name)
    def __str__(self):
        return (f"\nGuest Name:{self.__name}\nMobile Number:{self.__mobile_no}\nEmail:{self.__email}\nNumber of Guests:{self.__no_of_guests}")
# guest=Guest("Varshini","9876543210","varshini@gmail.com",3)
# print(guest)

class Booking:
    def __init__(self,booking_id,guest_id,rooms,guests,check_in,check_out,total_amount,booking_status):
        self.set_booking_id(booking_id)
        self.set_guest_id(guest_id)
        self.set_rooms(rooms)
        self.set_guests(guests)
        self.set_checkin(check_in)
        self.set_check_out(check_out)
        self.set_total_amount(total_amount)
        self.set_booking_status(booking_status)
        
    def set_booking_id(self,booking_id):
        if booking_id is None or str(booking_id).strip()=="":
            raise BookingNotFound("Booking id must not be empty")
        self.__booking_id=booking_id
    def get_booking_id(self):
        return self.__booking_id
    def set_guest_id(self,guest_id):
        if int(guest_id)<=0:
            raise ValueError("Invalid guest id")
        self.__guest_id=int(guest_id)
    def get_guest_id(self):
        return self.__guest_id
    
    def set_rooms(self,rooms):
        if not isinstance(rooms,(Room)):
            raise ValueError("Rooms object is not found")
        self.__rooms=rooms 
        self.__room_no=rooms.room_no
    def get_rooms(self):
        return self.__room_no   
    def set_guests(self,guests):
        if not isinstance(guests,Guest):
            raise ValueError("Guests object not found")
        self.__guests=guests
        self.__no_of_guests=guests.get_noofguests()
    def set_guest(self):
        return self.__no_of_guests
    
    def set_checkin(self,check_in):
        try:
            check_in=datetime.strptime(check_in,'%d-%m-%Y').date()
        except ValueError:
            raise InvalidDate("Invalid check_in format")
        today=date.today()
        if check_in<today:
            raise InvalidDate("Check_in cannot be in past")
        if check_in>today+timedelta(days=180):
            raise InvalidDate("Check_in cannot be more than 180 days")
        self.__check_in=check_in
    def get_check_in(self):
        return self.__check_in
    def set_check_out(self,check_out):
        try:
            check_out=datetime.strptime(check_out,"%d-%m-%Y").date()
        except ValueError:
            raise InvalidDate("Invalid check_in format")
        if check_out<=self.__check_in:
            raise InvalidDate("Check out must be later than check in")
        nights=(check_out-self.__check_in).days
        if nights<1 or nights>30:
            raise InvalidDate("stay must be between 1 and 30 nights")
        self.__check_out=check_out
    def get_check_out(self):
        return self.__check_out   
    def set_total_amount(self,total_amount):
        total_amount=float(total_amount)
        if total_amount<0:
            raise ValueError("total amount must be greater than 0")
        self.__total_amount=total_amount 
    def get_total_amount(self):
        return self.__total_amount
    def set_booking_status(self,booking_status):
        if booking_status not in ["CONFIRMED","CHECKED_IN","CHECKED_OUT","CANCELLED"]:
            raise InvalidStatus("Invalid booking status")
        self.__booking_status=booking_status
    def get_booking_status(self):
        return self.__booking_status
    
    def change_status(self,new_status):
        transitions={
            "CONFIRMED":["CHECKED_IN","CANCELLED"],
            "CHECKED_IN":["CHECKED_OUT"],
            "CHECKED_OUT":[],
            "CANCELLED":[]
        }
        if new_status not in transitions:
            raise InvalidStatus("Invalid booking status")
        if new_status not in transitions.get(self.__booking_status,[]):
            raise InvalidStatus("Invalid status transition")
        self.__booking_status=new_status
    # def __str__(self):
    #     return (f"\nBooking ID:{self.__booking_id}\nGuest ID:{self.__guest_id}"
    #         f"\nRoom Number:{self.__room_no}\nCheck-in:{self.__check_in}"
    #         f"\nCheck-out:{self.__check_out}\nNumber of Guests:{self.__no_of_guests}"
    #         f"\nTotal Amount:{self.__total_amount}\nBooking Status:{self.__booking_status}")

# booking=Booking("01","1","101","1","4-11-2026","6-11-2026","4500","CHECKED_IN")