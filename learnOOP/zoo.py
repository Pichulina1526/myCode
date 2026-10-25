
class Animal:
    def __init__(self,name,age,weight):
        self.__name = name
        self.__age = age
        self.__weight = weight

    def get_age(self):
        return self.__age

    def increment_age(self):
        self.__age += 1

    def get_name(self):
        return self.__name

    def get_weight(self):
        return self.__weight

    def set_weight(self,new_weight):
        self.__weight = new_weight


    def make_sound(self):
        print("I am hungry and want food")

class Bird(Animal):
    def __init__ (self,name,age,weight,wingspan,top_speed):
        super().__init__(name,age,weight)
        self.__wingspan = wingspan
        self.__top_speed = top_speed

    def make_sound(self):
        super().make_sound()
        print("I am a bird")


bird1 = Bird("theo",10,50,1.8,85)
weight = bird1.get_weight()
print(weight)
bird1.make_sound()