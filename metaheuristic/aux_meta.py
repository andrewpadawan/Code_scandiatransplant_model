import pandas as pd
import ast

import pandas as pd

payback_debts_transposed = pd.DataFrame({
    "Aarhus": {
        "Aarhus": [],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Copenhagen": {
        "Aarhus": [],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Odense": {
        "Aarhus": [("O", 62)],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [("O", 59)],
        "Tartu": []
    },
    "Skane": {
        "Aarhus": [],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [("O", 66)],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Gothenburg": {
        "Aarhus": [],
        "Copenhagen": [("O", 35)],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Stockholm": {
        "Aarhus": [],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Uppsala": {
        "Aarhus": [("O", 49)],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Oslo": {
        "Aarhus": [],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Reykjavik": {
        "Aarhus": [],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Helsinki": {
        "Aarhus": [],
        "Copenhagen": [],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [],
        "Tartu": []
    },
    "Tartu": {
        "Aarhus": [],
        "Copenhagen": [("O", 49)],
        "Odense": [],
        "Skane": [],
        "Gothenburg": [],
        "Stockholm": [],
        "Uppsala": [],
        "Oslo": [],
        "Reykjavik": [],
        "Helsinki": [("O", 85)],
        "Tartu": []
    }
})


