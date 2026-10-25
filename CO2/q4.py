students = int(input("enter the number of students"))
books = int(input("enter number of books"))

booksPerPerson = books // students

booksLeftOver = books % students

print(f"each student will get {booksPerPerson} books and there will be {booksLeftOver} books left over")

