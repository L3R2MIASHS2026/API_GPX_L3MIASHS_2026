import folium
from models import Trail
import requests as rq
from services import GPXParser
import HTMLResponse


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


def map_traces(min_dist:int = 0 ,max_dist:int = 150,):
    m = folium.Map()
    all_points = []
    liste_trail = rq.get(f'https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist={min_dist}&max_dist={max_dist}')
    if liste_trail:
        for trail in liste_trail:
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

        folium.LayerControl().add_to(m)

    return HTMLResponse(content=m._repr_html_())






map_traces()
map_traces(3,15)
