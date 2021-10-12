import random

class Random:
    def random_bool_value(self):
        a = random.randrange(0,2)
        return (a == 1)
        
    def random_int_value_with_range(self, min: int, max: int):
        return random.randint(min, max)
    
    def random_float_value_with_range(self, min: float, max: float):
        return round(random.uniform(min, max), 1)
