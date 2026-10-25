
# class def

class Rectangle:
    def __init__(self, width, height):
        self.__width = width
        self.__height = height


    # getters
    @property
    def width(self):
        return f"{self.__width:.1f}cm"

    @property
    def height(self):
        return f"{self.__height:.1f}cm"

    # setters
    @width.setter
    def width(self, new_width):
        if new_width > 0:
            self.__width = new_width
        else:
            print("invalid length! ")

    @height.setter
    def height(self, new_height):
        if new_height > 0:
            self.__height = new_height
        else:
            print("invalid length")

    def area(self):
        x = (self.__height * self.__width)
        return x


height_x = int(input("enter height: "))
width_x = int(input("enter width: "))
#rectangle_name = input("enter name for rectangle: ")

rectangle1 = Rectangle(width_x, height_x)

choice = 0
while choice != 4:
    choice = int(input("do you want to: 1. find area   2. change height   3. change width  4.exit : "))

    if choice == 1:
        area = rectangle1.area()
        print(f"The area of the rectangle is {area}")
    elif choice == 2:
        new_height = int(input("enter new height: "))
        rectangle1.height = new_height
    elif choice == 3:
        new_width = int(input("enter new width: "))
        rectangle1.width = new_width
