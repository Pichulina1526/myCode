class Car:
    def __init__(self, model, year, colour, for_sale,mileage):
        self.model = model
        self.year = year
        self.colour = colour
        self.for_sale = for_sale
        self.__mileage = mileage

    def get_mileage(self):
        return self.__mileage
        
    def drive(self):
        print(f"You drive the {self.model}")
        
    def stop(self):
        print(f"you stop the {self.model}")
        
    def describe(self):
        print(f"{self.year} {self.colour} {self.model}")


