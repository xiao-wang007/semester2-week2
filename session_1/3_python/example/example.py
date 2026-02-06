import sqlite3

def get_connection(db_path="university.db"):
    """
    Establish a connection to the SQLite database.
    Returns a connection object.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows access by column name
    return conn

def menu():
    '''
    Prints menu and prompts for choice
    Returns choice (string)
    '''
    print("1 - Search for Student")
    print("2 - View Department")
    print("3 - View Courses")
    print("4 - View Students by Course")
    print("5 - View Number of Students per Course")
    print("Q - quit")
    choice = -1
    while (choice not in ["1","2","3","4","5","Q"]):
        choice = input("Enter your choice: ").upper()
    return choice

def search_for_student(db):
    '''
    Allows a user to search for one student by name or id.
    
    :param db: database object to run queries on
    '''
    choice = input("Enter student name or ID number: ")
    try: # we need to convert the id number to int, and we can use this to decide id or name.
        choice = int(choice)
        query = '''
                SELECT s.department_id, s.name, d.name
                FROM Students s JOIN Department d
                ON s.id=d.id
                WHERE s.id=?
                '''
    except:
        query = '''
                SELECT s.id, s.name, d.name
                FROM Students s JOIN Department d
                ON s.department_id=d.id
                WHERE s.name=?
                '''
        
    # first we run the query, providing a tuple of any ? values.
    cursor = db.execute(query, (choice,))
    # we can then fetch our result from the cursor
    # this gives us the row as a tuple
    student = cursor.fetchone()

    # and we ensure that we did find a result.
    if student:
        print(f"ID: {student[0]}\tName: {student[1]}\tDepartment: {student[2]}")
    else:
        print(f"Student {choice} not found.")



def view_dept(db):
    '''
    Shows all department IDs and names
    
    :param db: database object to query
    '''
    query = "SELECT id, name FROM Department;"
    cursor = db.execute(query)
    # where we know we should have multiple results, we can iterate over the cursor.
    for dept in cursor:
        print(f"ID: {dept[0]}\tName: {dept[1]}")

def view_courses(db):
    '''
   Shows all courses with id, name, semester and department name.
    
    :param db: db object to query
    '''
    query = '''
            SELECT c.id, c.name, c.semester, d.name FROM
            Courses c LEFT JOIN Department d
            ON c.id=d.id;
            '''
    cursor = db.execute(query)
    for each in cursor:
        print(f"ID: {each[0]}\tName: {each[1]}\tSemester: {each[2]}\tDept: {each[3]}")

def view_student_by_course(db):
    choice = -1
    while(choice < 1):
        choice = input("Enter course ID: ")
        try:
            choice = int(choice)
        except:
            choice=-1
    query = '''
            SELECT s.name from
            StudentCourses sc 
            JOIN Students s ON
            student_id=s.id
            WHERE sc.course_id=?;
            '''
    cursor = db.execute(query, (choice,))
    for student in cursor:
        print(f"Name: {student[0]}")


# Have a go at writing this function!
def review_student_numbers(db):
    '''
    Print the number of students registered for each course.    
    :param db: Database object to query
    '''
    query = '''
            SELECT c.name, COUNT(sc.student_id) AS student_count
            FROM Courses c
            LEFT JOIN StudentCourses sc ON c.id = sc.course_id
            GROUP BY c.id;
            '''
    cursor = db.execute(query)
    for course in cursor:
        print(f"Course: {course[0]}\tStudents: {course[1]}")

def main():

    db = get_connection()

    while 1:
        choice = menu()
        match(choice):
            case "1":
                search_for_student(db)

            case "2":
                view_dept(db)

            case "3":
                view_courses(db)

            case "4":
                view_student_by_course(db)
            
            case "5":
                review_student_numbers(db)

            case "Q":
                exit()



    # Always close your database connection at the end!
    db.close()


if __name__=="__main__":
    main()
