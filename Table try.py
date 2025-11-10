import sqlite3

connection = sqlite3.connect('hotel.db')
cursur = connection.cursor()

command1 = """create table if not exists
room_management(room_id integer primary key, price integer, status text)"""

cursur.execute(command1)

command2 = """create table if not exists
reservation(reservation_id integer primary key, name text, contact text, room_id integer, 
foreign key(room_id) references room_management(room_id))"""

cursur.execute(command2)

cursur.execute("insert into room_management values (101, 10, 'available')")
cursur.execute("insert into room_management values (102, 10, 'occupied')")

cursur.execute("insert into reservation values (1, 'euigwapo', '09940018283', 102)")

cursur.execute("select * from reservation")

result = cursur.fetchall()
print(result)