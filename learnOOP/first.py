
from car import Car


        
car1 = Car("AMG gt",2020,"black",True,500)

print(car1.model)
car1.drive() 
car1.describe()

miles = car1.get_mileage()
print(miles)