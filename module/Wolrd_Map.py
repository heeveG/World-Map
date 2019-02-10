import folium
from tqdm import tqdm
import geocoder


def create_map(films, max_movies, n):
    """
    (dict, dict, int) -> None
    Function gets all collected info about films and makes a map
    1. dict with movie as a key and location coords as value
    2. dict with movie as a key and movies filmed in n year
    3. integer representing year that is explored
    """
    map = folium.Map(location=[48.314775, 25.082925], zoom_start=1, \
                    tiles='cartodbpositron')

    area = folium.FeatureGroup(name="Population. (Click on map for info)")
    area.add_child(folium.GeoJson(data=open('world.json', 'r', \
                    encoding='utf-8-sig').read(), style_function=lambda x: \
                    {'fillColor': 'red' if x['properties']['AREA']\
                      <= 50000 else 'orange' if 50000 < \
                      x['properties']['AREA'] <= 500000 else 'green'}))
    area.add_child(folium.Popup('Country Area : Red <= 500000 sqkm |\
                                Orange <= 5000000 sqkm | Red > 5000000 sqkm'))
    flm = folium.FeatureGroup(name="Movies filmed in {}".format(n))
    for key, value in films.items():
        try:
            flm.add_child(folium.Marker(location=[value[1][0],\
                         value[1][1]], popup='{}. {}  Filmed in : {}'\
                         .format(key, '\n', value[0], icon=folium.Icon())))
        except:
            pass
    top_cntr = folium.FeatureGroup(name="Country(ies) with the biggest number\
                                    of new movies in {}".format(n))
    for i in max_movies:
        top_cntr.add_child(folium.CircleMarker(location=(i),\
                            radius= 25, color="black"))
    map.add_child(area)
    map.add_child(flm)
    map.add_child(top_cntr)
    map.add_child(folium.LayerControl())
    map.save('WolrdMap_{}.html'.format(n))


def read_file(filename, year):
    """
    (str, int) -> dict
    Returns a dict with movie, that was filmed in given year as a key and
    location as value
    e.g.: >>> read_file('file', 2015)
    {"Movie" : [USA], "Film" : [Mexico]}
    """
    f = open(filename, encoding='utf-8', errors='ignore')
    films = dict()
    for line in f:
        if '({})'.format(str(year)) in line:
            splt = line.split('\t')
            if "(" in splt[-1]:
                splt.pop()
            movieName = splt[0].split('(')[0]
            if movieName not in films.keys():
                films[movieName] = [splt[-1].replace("\n", "")]

    f.close()
    return films


def get_location(films):
    """
    (dict) -> (dict, list)
    Finds latitude and longtitude for each movie in given dict.
    Finds country(ies) with the most movies filmed

    >>> print(get_location({'Unknown' : ["USA"]}))
    ({'Unknown': ['USA', [39.39870315600007, -99.41461918999994]]}, \
[[39.39870315600007, -99.41461918999994]])
    """
    new_dict = {}
    for key, value in tqdm(films.items()):
        if value[0].split(',')[-1] not in new_dict.keys():
            new_dict[value[0].split(',')[-1]] = 1
        else:
            new_dict[value[0].split(',')[-1]] += 1
        location = geocoder.arcgis(value[0]).latlng
        value.append(location)
    top_cntr = []
    for key, value in new_dict.items():
        if value == max(new_dict.values()):
            top_cntr.append(geocoder.arcgis(key).latlng)
    return (films, top_cntr)


if __name__ == "__main__":
    n = int(input("Enter a year to discover where were \
filmed movies during that time:\n"))
    films = read_file('locations.list', n)
    mvs = get_location(films)
    create_map(mvs[0], mvs[1], n)
