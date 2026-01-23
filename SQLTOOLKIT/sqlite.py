import sqlite3 as sql

# Koneksi ke database
connection = sql.connect("student.db")

# Membuat cursor
cursor = connection.cursor()

# Membuat Tabel student
table_info = """
    create table STUDENT(NAME VARCHAR(25), CLASS VARCHAR(25), SECTION VARCHAR(25), MARKS INT)
"""

cursor.execute(table_info)

## Insert Records
cursor.execute('''Insert Into STUDENT values('Farhan', 'AI Engineer', 'A', 92)''')
cursor.execute('''Insert Into STUDENT values('Keynissa', 'AI Engineer', 'B', 60)''')
cursor.execute('''Insert Into STUDENT values('Farhan', 'Data Science', 'A', 87)''')
cursor.execute('''Insert Into STUDENT values('Keynissa', 'Gambar Teknik', 'A', 100)''')
cursor.execute('''Insert Into STUDENT values('Kori', 'AI Engineer', 'A', 82)''')

## Display the data
print("data yang sudah dimasukkan adalah: ")
data = cursor.execute("SELECT * FROM STUDENT")
for row in data:
    print (row)

## perubahan pada database
connection.commit()
connection.close()

