import folium
import requests as rq
from services import GPXParser
from fastapi.responses import HTMLResponse
from geopy.distance import geodesic 
import webbrowser
import os




def generate_trail_map(trail: Trail) -> str:
    """
    Génère le code HTML d'une carte Folium à partir d'un objet Trail.
    """
    # 1. Sécurité : on vérifie si la trace a des points
    if not trail.points or len(trail.points) == 0:
        return "<p style='color:red; font-family:sans-serif;'>Aucun point GPS disponible pour cette trace.</p>"

    # 2. Trier les points par leur champ 'order' pour éviter les zigzags
    sorted_points = sorted(trail.points, key=lambda p: p.order)

    # 3. Créer la liste de coordonnées [(lat1, lon1), (lat2, lon2), ...]
    coordinates = [(pt.latitude, pt.longitude) for pt in sorted_points]

    # 4. Initialiser la carte centrée sur le point de départ
    start_loc = coordinates[0]
    m = folium.Map(
        location=start_loc,
        zoom_start=14,
        tiles="OpenStreetMap"  # Fond de carte standard
    )

    # 5. Dessiner le tracé (PolyLine)
    folium.PolyLine(
        locations=coordinates,
        color="#3388ff",  # Bleu vif
        weight=5,
        opacity=0.8,
        tooltip=f"Parcours : {trail.name}"
    ).add_to(m)

    # 6. Ajouter les marqueurs de début et de fin
    # Départ en Vert
    folium.Marker(
        coordinates[0],
        popup="Départ",
        icon=folium.Icon(color="green", icon="play")
    ).add_to(m)

    # Arrivée en Rouge
    folium.Marker(
        coordinates[-1],
        popup="Arrivée",
        icon=folium.Icon(color="red", icon="stop")
    ).add_to(m)

    # 7. Retourner le HTML de la carte
    # Cette méthode génère tout le JS et le CSS nécessaire
    return HTMLResponse(content=m._repr_html_())



def get_trail_points(trail: Trail, step=1):
    _, points = GPXParser.parse_gpx(trail.gpx_content)
    liste_lonlat = [[pts.latitude, pts.longitude] for pts in points]
    if step > 1:
        return liste_lonlat[::step]
    else:
        return liste_lonlat



def map_traces_by_distance(min_dist:int = 0 ,max_dist:int = 150):
    liste_trail = rq.get(f'https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist={min_dist}&max_dist={max_dist}')
    map_traces(liste_trail)


def map_traces(liste_trail):
    m = folium.Map(
        control_scale=True)
    all_points = []
    
    if liste_trail:
        for trail in liste_trail:
            liste_lonlat = get_trail_points(trail,3)

            folium.PolyLine(
                liste_lonlat,
                tooltip=trail.name,
                color="blue",
                weight=3,
            ).add_to(m)

            all_points.extend(liste_lonlat)

        m.fit_bounds(all_points, padding=(30, 30))  ##centrage du zoom


    m.save("map.html")

    webbrowser.open("file://" + os.path.realpath("map.html"))

def map_by_hardness(easy = True, medium = True, hard = True, online  = True):

    if online:
        all_trail = rq.get('https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist=0&max_dist=150')
    else:
        all_trail = rq.get('http://127.0.0.1:8000/docs/traces?min_dist=0&max_dist=150')    
    
    easy_trails, medium_trails,hard_trails = sort_trail_by_hardness(all_trail)

    m = folium.Map(
        control_scale=True)
    
    all_points = []
    

    if easy:
        all_points = lines_for_map(easy_trails, m ,all_points,"green")
    if medium:
        all_points  = lines_for_map(medium_trails, m ,all_points,"orange")
    if hard:
        all_points  = lines_for_map(hard_trails, m ,all_points,"red")

    m.fit_bounds(all_points, padding=(30, 30))  ##centrage du zoom


    m.save("map.html")

    webbrowser.open("file://" + os.path.realpath("map.html"))

     


def lines_for_map(liste, carte,all_points, col="blue"):
    if liste:
        for trail in liste:
            liste_lonlat = get_trail_points(trail,3)

            folium.PolyLine(
                liste_lonlat,
                tooltip=trail.name,
                color=col,
                weight=3,
            ).add_to(carte)

            all_points.extend(liste_lonlat)
    return all_points


    

def sort_trail_by_hardness(liste_trail):
    easy_trails = []
    medium_trails = []
    hard_trails = []
    for trail in liste_trail:
        if (trail.elevation_gain >= 500 and trail.length >=5000) or trail.length>=25000:
            hard_trails.append(trail)
        elif (trail.elevation_gain >=200 and trail.length >=5000) or trail.length>=15000:
            medium_trails.append(trail)
        else:
            easy_trails.append(trail)
    return easy_trails, medium_trails,hard_trails










    




    




