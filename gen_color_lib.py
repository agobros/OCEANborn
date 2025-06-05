import json

color_dict = {}

color_dict['cycler'] = ['#4169E1', #royal blue4169E1
        "#66CC66", #green
        '#fc6600', #orange 
        '#CC0033', #red
        '#be29ec', #purple
        '#ff00a9', #pink
        '#006600'] #dark green

json.dump(color_dict, open('oceanborn\\_lib\\colors.json', 'w'), indent=4)