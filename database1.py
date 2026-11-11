import sqlite3
from datetime import datetime,timedelta
def create_connection():
    conn=sqlite3.connect("booking.db")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def create_tables():
    conn=create_connection()
    cur=conn.cursor()
    # cur.execute("drop table if exists bookings")
    # cur.execute("drop table if exists guests")
    # cur.execute("drop table if exists rooms")
    # cur.execute("drop table if exists bookings")
    cur.execute("""CREATE TABLE IF NOT EXISTS guests(guest_id INTEGER PRIMARY KEY AUTOINCREMENT,
        mobile_no TEXT UNIQUE NOT NULL,name TEXT NOT NULL,
        email TEXT NOT NULL,
        no_of_guest INTEGER NOT NULL,
        registration_count INTEGER NOT NULL DEFAULT 1)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS rooms(
        room_no INTEGER PRIMARY KEY,
        room_type TEXT NOT NULL,
        floor INTEGER NOT NULL,
        base_rate REAL NOT NULL,
        max_guest INTEGER NOT NULL,
        availability INTEGER NOT NULL DEFAULT 1)""")
    cur.execute("""CREATE TABLE IF NOT EXISTS bookings(
    booking_id INTEGER PRIMARY KEY AUTOINCREMENT,
    guest_id INTEGER NOT NULL,
    room_no INTEGER NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    no_of_guests INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    booking_status TEXT NOT NULL,
    room_revenue REAL DEFAULT 0,
    gst_amount REAL DEFAULT 0,
    refund_amount REAL DEFAULT 0,
    FOREIGN KEY(room_no) REFERENCES rooms(room_no),
    FOREIGN KEY(guest_id) REFERENCES guests(guest_id))""")
    conn.commit()
    conn.close()

def insert_guest(mobile_no,name,email,no_of_guest):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""INSERT INTO guests(mobile_no,name,email,no_of_guest)
        VALUES(?,?,?,?)""",(mobile_no,name,email,no_of_guest))
    guest_id=cur.lastrowid
    conn.commit()
    conn.close()
    return guest_id
    
def find_guest_by_mobile(mobile_no):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("SELECT * FROM guests WHERE mobile_no=?",
                (mobile_no,))
    result=cur.fetchone()
    conn.close()
    return result

def insert_valid_rooms(rooms_objects):
    room_records=[]
    for room in rooms_objects:
        room_records.append(
            (
                room.room_no,
                room.room_type,
                room.floor,
                room.get_base_rate(),
                room.get_max_guests()
            ))
    conn=create_connection()
    cur=conn.cursor()
    cur.executemany("""INSERT OR IGNORE INTO rooms(
        room_no,room_type,floor,base_rate,max_guest)
        VALUES(?,?,?,?,?)""",room_records)
    inserted_count=cur.rowcount
    conn.commit()
    conn.close()
    return inserted_count

def get_all_rooms():
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("SELECT * FROM rooms ORDER BY room_no")
    result=cur.fetchall()
    conn.close()
    return result

def search_availability(room_type,check_in_db,check_out_db,no_of_guests):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""select r.room_no,r.room_type,r.floor,r.base_rate,r.max_guest
                from rooms r
                LEFT JOIN bookings b
                ON r.room_no=b.room_no
                AND b.check_in < ?
                AND b.check_out>?
                AND b.booking_status not in ("CANCELLED","CHECKED_OUT")
                where r.room_type=? AND r.max_guest>=? AND b.booking_id is NULL
                ORDER BY r.room_no""",(check_out_db,check_in_db,room_type,no_of_guests))
    result=cur.fetchall()
    conn.close()
    return result

def get_room_details(room_no):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""SELECT room_no,room_type,floor,base_rate,max_guest FROM rooms WHERE room_no=?""",(room_no,))
    room=cur.fetchone()
    conn.close()
    if room is None:
        return None
    return {
        "room_no":room[0],
        "room_type":room[1],
        "floor":room[2],
        "base_rate":room[3],
        "max_guest":room[4]
    }

def allocate_room(room_type,no_of_guests,check_in_db,check_out_db,rooms_objects):
    available_rooms=search_availability(room_type,check_in_db,check_out_db,no_of_guests)
    if available_rooms:
        room_no=available_rooms[0][0]
        for room in rooms_objects:
            if room.room_no==room_no:
                return room
    print("No rooms available for requested type")
    alternative_rooms=[]
    for alternative_type in ["Standard","Deluxe","Suite"]:
        if alternative_type==room_type:
            continue
        alternative_rooms.extend(search_availability(
            alternative_type,check_in_db,check_out_db,no_of_guests))
        if alternative_rooms:
            print("\nAvailable Alternative rooms:")
            for room in alternative_rooms:
                print("Room Number:",room[0],"Room Type:",room[1])
        else:
            print("No alternative Rooms")
        return None
    
def insert_booking(guest_id,room_no,check_in,check_out,
                no_of_guests,room_revenue,gst_amount,booking_status="CONFIRMED"):
    total_amount=room_revenue+gst_amount
    refund_amount=0
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""INSERT INTO bookings(
        guest_id,room_no,check_in,check_out,no_of_guests,total_amount,booking_status,
        room_revenue,gst_amount,refund_amount)
        VALUES(?,?,?,?,?,?,?,?,?,?)""",
        (guest_id,room_no,check_in,check_out,no_of_guests,total_amount,booking_status,
        room_revenue,gst_amount,refund_amount))

    booking_id=cur.lastrowid
    conn.commit()
    conn.close()
    return booking_id

def get_bookings():
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("select * from bookings Order by booking_id")
    result=cur.fetchall()
    conn.close()
    return result
# get_bookings()

def get_book_details(book_id):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""SELECT b.booking_id,b.guest_id,b.room_no,b.check_in,b.check_out,b.no_of_guests,
                b.total_amount,b.booking_status,r.room_type,r.base_rate ,
                g.name,g.mobile_no
                FROM bookings b
                JOIN rooms r on b.room_no=r.room_no
                JOIN guests g on g.guest_id=b.guest_id
                WHERE booking_id=?""",(book_id,))
    booking=cur.fetchone()
    conn.close()
    return booking

def get_completed_stays(guest_id):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""SELECT COUNT(*) FROM bookings
        WHERE guest_id=?
        AND booking_status='CHECKED_OUT'""",(guest_id,))

    count=cur.fetchone()[0]
    conn.close()
    return count

def update_booking_status(booking_id,status):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""
        UPDATE bookings SET booking_status=?
        WHERE booking_id=?""",(status,booking_id))
    updated=cur.rowcount
    conn.commit()
    conn.close()
    return updated

def get_guest_stay_history(guest_id):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""Select booking_id,room_no,check_in,check_out,total_amount,booking_status
                from bookings where guest_id=? order by check_in""",(guest_id,))
    result=cur.fetchall()
    conn.close()
    return result
# def get_occupancy_report():
#     conn=create_connection()
#     cur=conn.cursor()
#     cur.execute("""SELECT r.room_no,r.room_type,
#                 COUNT(b.booking_id) AS booking_count
#                 FROM rooms r LEFT JOIN bookings b
#                 ON r.room_no=b.room_no
#                 AND b.booking_status in ('CONFIRMED','CHECKED_IN','CHECKED_OUT')
#                 GROUP BY r.room_no,r.room_type
#                 ORDER BY r.room_no""")
#     result=cur.fetchall()
#     conn.close()
#     return result

def get_occupancy_report(start_date,end_date):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("select count(*) from rooms")
    total_rooms=cur.fetchone()[0]
    if total_rooms==0:
        conn.close()
        return [],0
    
    current_date=datetime.strptime(start_date,"%Y-%m-%d").date()
    last_date=datetime.strptime(end_date,"%Y-%m-%d").date()
    result=[]
    total_percent=0
    nights=0
    while current_date<last_date:
        date_str=current_date.strftime("%Y-%m-%d")
        cur.execute("""select COUNT(distinct room_no) from bookings where check_in <= ?
                    AND check_out>? AND booking_status != 'CANCELLED'""",(date_str,date_str))
        occupied=cur.fetchone()[0]
        percentage=(occupied/total_rooms)*100
        result.append((date_str,occupied,total_rooms,percentage))
        total_percent+=percentage
        nights+=1
        current_date+=timedelta(days=1)
    average=total_percent/nights if nights>0 else 0
    conn.close()
    return result,average

def cancel_booking_record(booking_id,refund_amount):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""UPDATE bookings SET booking_status=?,refund_amount=?
        WHERE booking_id=?""",("CANCELLED",refund_amount,booking_id))
    conn.commit()
    conn.close()

def get_revenue():
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""SELECT r.room_type,
            COUNT(CASE WHEN b.booking_status='CHECKED_OUT' THEN 1 END),
            COALESCE(SUM(CASE WHEN b.booking_status='CHECKED_OUT'
                THEN b.room_revenue ELSE 0 END),0),
            COALESCE(SUM(CASE WHEN b.booking_status='CHECKED_OUT'
                THEN b.gst_amount ELSE 0 END),0),
            COALESCE(SUM(CASE WHEN b.booking_status='CANCELLED'
                THEN b.total_amount-b.refund_amount ELSE 0 END),0)
        FROM rooms r
        LEFT JOIN bookings b ON r.room_no=b.room_no
        GROUP BY r.room_type
    """)
    result=cur.fetchall()
    conn.close()
    return result

def get_invoice_data(booking_id):
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("""
        SELECT b.booking_id,g.name,g.mobile_no,g.email,
            r.room_no,r.room_type,b.check_in,b.check_out,
            b.no_of_guests,b.room_revenue,
            b.gst_amount,b.total_amount
        FROM bookings b
        JOIN guests g ON b.guest_id=g.guest_id
        JOIN rooms r ON b.room_no=r.room_no
        WHERE b.booking_id=?
    """,(booking_id,))
    result=cur.fetchone()
    conn.close()
    return result

def check_tables():
    conn=create_connection()
    cur=conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print(cur.fetchall())

    conn.close()
create_tables()
check_tables()