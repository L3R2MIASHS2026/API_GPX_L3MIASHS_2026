import folium
from models import Trail
from services import GPXparser

def map_traces(trails :list[type[Trail]]):
    m = folium.Map()
    all_points = []
    for trail in trails:
        liste_lonlat = get_trail_points(trail,3)

        fg = folium.FeatureGroup(name=trail.name) ## afin que chaque trail soit une couche indépendantes

        folium.PolyLine(
            liste_lonlat,
            tooltip=trail.name,
            color="blue",
            weight=3,
        ).add_to(fg)

        fg.add_to(m)
        all_points.extend(liste_lonlat)

        m.fit_bounds(all_points, padding=(30, 30))  ##centrage du zoom
        
        folium.LayerControl().add_to(m) ## permet de gérer les différentes couches créer





@staticmethod
def get_trail_points(trail: Trail, step=1):
    _, points = GPXParser.parse_gpx(trail.gpx_content)
    liste_lonlat = [[pts.longitude, pts.latitude] for pts in points]
    if step > 1:
        return liste_lonlat[::step]
    else:
        return liste_lonlat

