import random, string, json
from pathlib import Path

class Student:
    database = 'students.json'
    data = []

    try:
        if Path(database).exists():
            with open(database) as fs:
                data = json.loads(fs.read())
        else:
            with open(database, 'w') as fs:
                fs.write('[]')
    except Exception as err:
        print(f"An error occured as {err}")

    @staticmethod
    def __generatestudentid():
        alpha = random.choices(string.ascii_letters, k = 7)
        num = random.choices(string.digits, k = 4)
        spchr = random.choices("!@#$%&", k =1)
        id = alpha + num + spchr
        random.shuffle(id)
        return "".join(id).capitalize()
    
    @classmethod
    def __update(cls):
        with open(cls.database, 'w') as fs:
            fs.write(json.dumps(Student.data))

    def addstudent(self):
        info = {
            'name' : input("Enter student's full name: "),
            'email' : input("Enter student's email address: "),
            'age' : int(input("Enter student's age: ")),
            'studentid' : Student.__generatestudentid(),
            'courses' : input("Enter the courses[add comma for every course]: "),
            'grades' : input("Enter student's grade: ")
        }
        if info['age'] < 8:
            print("Age must be 10 or above.")
        else:
            print("Student's Account has been created.")
            print("\n")
            for i in info:
                print(f"{i}: {info[i]}")
            print("Please Note down your student id")
            Student.data.append(info)
            Student.__update()

    def updatestudent(self):
        stuid = input("Enter student's id: ")
        studdata = [i for i in Student.data if i['studentid'] == stuid]
        if not studdata:
            print("Sorry no student found.")
        else:
            print("\n")
            print("Fill out the details to update student's details.")
            newdata = {
                'name' : input("Enter new student's full name or press enter to skip: "),
                'email' : input("Enter new student's email or press enter to skip: "),
                'courses' : input("Enter new courses or press enter to skip: ")
            }
            if newdata['name'] == "":
                newdata['name'] = studdata[0]['name']
            if newdata['email'] == "":
                newdata['email'] = studdata[0]['email']
            if newdata['courses'] == "":
                newdata['courses'] = studdata[0]['courses']
            newdata['age'] = studdata[0]['age']
            newdata['grades'] = studdata[0]['grades']

            for i in newdata:
                if newdata[i] == studdata[0][i]:
                    continue
                else:
                    studdata[0][i] = newdata[i]
            Student.__update()
            print("\n")
            print("Student's details updated successfully.")
            for i in studdata[0]:
                print(f"{i}: {studdata[0][i]}")
            print("\n")

    def viewstudent(self):
        stuid = input("Enter student's id: ")
        studdata = [i for i in Student.data if i['studentid'] == stuid]
        if studdata == False:
            print("Sorry no data found.")
        else:
            print("*********************")
            print("Student's information")
            for i in studdata[0]:
                print(f"{i}: {studdata[0][i]}")

            print("\n")

    def removestudent(self):
        stuid = input("Enter student's id: ")
        studdata = [i for i in Student.data if i['studentid'] == stuid]
        if studdata == False:
            print("Sorry no data found.")
        else:
            delete = input("Enter 'y' to proceed/delete student's details or press 'n': ")
            if delete == 'n' or delete == 'N':
                print("Exits...")
            else:
                index = Student.data.index(studdata[0])
                Student.data.pop(index)
                print("****************")
                print("Student removed.")
                Student.__update()

    def viewall(self):
        studata = [i for i in Student.data]
        if studata == False:
            print("Sorry no data found.")
        else:
            print("**************************")
            print("All student's information.")
            print("-------------------------------------")
            for student in studata:
                print(f"Student: {student['name']}")
                print(f"Email: {student['email']}")
                print(f"Age: {student['age']}")
                print(f"Student Id: {student['studentid']}")
                print(f"Courses: {student['courses']}")
                print(f"Grades: {student['grades']}")
                print("-------------------------------------")
            print("***************************")



user = Student()
while True:
    print("")
    print("Press '1' to add student.")
    print("Press '2' to update student details.")
    print("Press '3' to view student's details.")
    print("Press '4' to remove student.")
    print("Press '5' to view all list of students.")
    print("Press '6' to exit.")
    try:
        resp = int(input("Enter your response: "))
    except Exception as err:
        print(f"An error occured as {err}")
    if resp == 1:
        user.addstudent()
    elif resp == 2:
        user.updatestudent()
    elif resp == 3:
        user.viewstudent()
    elif resp == 4:
        user.removestudent()
    elif resp == 5:
        user.viewall()
    elif resp == 6:
        print("----------------------")
        print("Quitting.... Good Bye!")
        print("----------------------")
        break
    else:
        print("Invalid response.")