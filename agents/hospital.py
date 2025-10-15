from book_keeping.locations import city_country_map

class Hospital:
    def __init__(self, name, city):
        self.name = name
        self.city = city
        self.country = city_country_map.get(city, "Unknown")
        self.local_waiting_list = {}
        