


city_country_map = {
    "Aarhus": "Denmark",
    "Copenhagen": "Denmark",
    "Odense": "Denmark",
    "Skane": "Sweden",
    "Gothenburg": "Sweden",
    "Stockholm": "Sweden",
    "Uppsala": "Sweden",
    "Oslo": "Norway",
    "Reykjavik": "Iceland",
    "Helsinki": "Finland",
    "Tartu": "Estonia"
}

"""city_data = {
    #numbers from wikipedia
    "Aarhus": {"country": "Denmark", "population": 1968469},
    "Copenhagen": {"country": "Denmark", "population": 2904705},
    "Odense": {"country": "Denmark", "population": 1241223},
    "Skane": {"country": "Sweden", "population": 1418496},  # Region, not a city
    "Gothenburg": {"country": "Sweden", "population": 674529},
    "Stockholm": {"country": "Sweden", "population": 1617407},
    "Uppsala": {"country": "Sweden", "population": 177074},
    "Oslo": {"country": "Norway", "population": 5606944},
    "Reykjavik": {"country": "Iceland", "population": 389444},
    "Helsinki": {"country": "Finland", "population": 5650325},
    "Tartu": {"country": "Estonia", "population": 1369995}
}"""

#used scandiatransplant info, estimated sweden's numbers
city_pop= {
    "Aarhus": 1968469,
    "Copenhagen": 2904705,
    "Odense": 1241223,
    "Skane": 2000000,
    "Gothenburg": 4000000,
    "Stockholm": 2500000,
    "Uppsala": 2100000,
    "Oslo": 5606944,
    "Reykjavik": 389444,
    "Helsinki": 5650325,
    "Tartu": 1369995
} 
city_pop_proportion={
    "Aarhus": 5.055,
    "Copenhagen": 7.459,
    "Odense": 3.187,
    "Skane": 5.136,
    "Gothenburg": 10.271,
    "Stockholm": 6.419,
    "Uppsala": 5.392,
    "Oslo": 14.397,
    "Reykjavik": 1.000,
    "Helsinki": 14.509,
    "Tartu": 3.518
    
}
# Static city coordinates (longitude, latitude)
CITY_COORDS_LONG_LAT = {
    "Aarhus": (56.1629, 10.2039),
    "Copenhagen": (55.6761, 12.5683),
    "Odense": (55.4038, 10.4024),
    "Skane": (55.604981, 13.003822),
    "Gothenburg": (57.7089, 11.9746),
    "Stockholm": (59.3293, 18.0686),
    "Uppsala": (59.8586, 17.6389),
    "Oslo": (59.9139, 10.7522),
    "Reykjavik": (64.1355, -21.8954),
    "Helsinki": (60.1695, 24.9354),
    "Tartu": (58.3776, 26.7290)
}

CITY_COORDS_LAT_LONG = {
    "Aarhus": (10.2039, 56.1629),
    "Copenhagen": (12.5683, 55.6761),
    "Odense": (10.4024, 55.4038),
    "Skane": (13.003822, 55.604981),
    "Gothenburg": (11.9746, 57.7089),
    "Stockholm": (18.0686, 59.3293),
    "Uppsala": (17.6389, 59.8586),
    "Oslo": (10.7522, 59.9139),
    "Reykjavik": (-21.8954, 64.1355),
    "Helsinki": (24.9354, 60.1695),
    "Tartu": (26.7290, 58.3776)
}
