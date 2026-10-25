
class Animal:
    def __init__(self,name):
        self.__name = name



    def get_name(self):
        return self.__name


class Dog(Animal):
    def make_sound(self):
        return ("woof")

class Cat(Animal):
    def make_sound(self):
        return ("meow")

class Dinosaur(Animal):
    def make_sound(self):
        return ("roaarrrr")


animals = [Dog("archie") , Cat("esme") , Dinosaur("tristan")]
for i in animals:
    print(f"{i.get_name()} says {i.make_sound()}")
