
# class def
class Animal:
    def __init__(self,breed,age):
        self.__breed = breed
        self.__age = age

    def get_breed(self):
        return self.__breed

    def get_age(self):
        return self.__age

    def sleep(self):
        print(f"This {self.get_breed()} is sleeping")


class Prey(Animal):
    def flee(self):
        print(f"This {self.get_breed()} is fleeing")

class Predator(Animal):
    def hunt(self):
        print(f"This {self.get_breed()} is hunting")

class Rabbit(Prey): #inherit
    pass

class Hawk(Predator):
    def __init__(self , age, top_speed):
        super().__init__("",age)
        self.__top_speed = top_speed

    def get_top_speed(self):
        return self.__top_speed

class Fish(Prey , Predator): # inherit from both
    pass

#prey , predator inherit from animal --> hawk,rabbit,fish inherit from both super classes
# main program


fish1 = Fish("koi",6)

fish1.flee()
fish1.hunt()
fish1.sleep()

hawk1 = Hawk(67,230)
print(f"top speed of hawk is {hawk1.get_top_speed()}")