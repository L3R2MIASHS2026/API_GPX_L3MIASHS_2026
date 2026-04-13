import folium
import requests as rq
from map_hardness import get_trail_points
from geopy.distance import geodesic 
import webbrowser
import os




def map_trail_by_point_and_startpoint(points, rayon_km, online = True ):
    m = folium.Map(
        control_scale=True)
    all_points = []
    if online:
        all_trail = rq.get('https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist=0').json()
    else:
        all_trail = rq.get('http://127.0.0.1:8000/docs/traces?min_dist=0').json()

    folium.Marker(
        location=points,
        
    ).add_to(m)

    if all_trail:
        for trail in all_trail:
            liste_lonlat = get_trail_points(trail)
            if geodesic(points,liste_lonlat[0]).kilometers <= rayon_km:

                folium.PolyLine(
                    liste_lonlat,
                    tooltip=trail["points"],
                    color="blue",
                    weight=3,
                ).add_to(m)

                all_points.extend(liste_lonlat)

        m.fit_bounds(all_points, padding=(30, 30))  ##centrage du zoom


    m.save("map.html")

    webbrowser.open("file://" + os.path.realpath("map.html"))



def map_trail_by_point_and_mean_point(points, rayon_km, online = True):
    m = folium.Map(
        control_scale=True)
    all_points = []
    if online:
        all_trail = rq.get('https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist=0').json()
    else:
        all_trail = rq.get('http://127.0.0.1:8000/docs/traces?min_dist=0').json()

    folium.Marker(
        location=points,
        
    ).add_to(m)

    
    if all_trail:
        for trail in all_trail:
            liste_lonlat = get_trail_points(trail)
            mean_coordinates = mean_point(liste_lonlat)    
            if geodesic(points,mean_coordinates).kilometers <= rayon_km:

                folium.PolyLine(
                    liste_lonlat,
                    tooltip=trail["name"],
                    color="blue",
                    weight=3,
                ).add_to(m)

                all_points.extend(liste_lonlat)


        m.fit_bounds(all_points, padding=(30, 30))  ##centrage du zoom


    m.save("map.html")

    webbrowser.open("file://" + os.path.realpath("map.html"))




def map_trail_by_point_and_one_point(points, rayon_km, online = True):
    m = folium.Map(
        control_scale=True)
    all_points = []
    if online:
        all_trail = rq.get('https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist=0').json()
    else:
        all_trail = rq.get('http://127.0.0.1:8000/docs/traces?min_dist=0').json()

    folium.Marker(
        location=points
        
    ).add_to(m)

    
    if all_trail:
        for trail in all_trail:
            liste_lonlat = get_trail_points(trail)
            for pts in liste_lonlat:
                if geodesic(points,pts).kilometers <= rayon_km:

                    folium.PolyLine(
                        liste_lonlat,
                        tooltip=trail["name"],
                        color="blue",
                        weight=3,
                    ).add_to(m)

                    all_points.extend(liste_lonlat)
                    break

        m.fit_bounds(all_points, padding=(30, 30))  ##centrage du zoom


    m.save("map.html")

    webbrowser.open("file://" + os.path.realpath("map.html"))


def mean_point(liste_lonlat):
    s1 = 0
    s2 = 0
    for point in liste_lonlat:
        s1+=point[0]
        s2+=point[1]
    return [s1/len(liste_lonlat),s2/len(liste_lonlat)] 



map_trail_by_point_and_startpoint([45.7484600, 4.8467100], 100, online = True)

import folium
import requests as rq
from services import GPXParser
from fastapi.responses import HTMLResponse
from map_hardness import get_trail_points
from geopy.distance import geodesic 
import webbrowser
import os




def map_trail_by_point_and_startpoint(points, rayon_km, online = True ):
    m = folium.Map(
        control_scale=True)
    all_points = []
    if online:
        all_trail = rq.get('https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist=0&max_dist=150').json()
    else:
        all_trail = rq.get('http://127.0.0.1:8000/docs/traces?min_dist=0&max_dist=150').json()

    folium.Marker(
        location=points,
        
    ).add_to(m)

    if all_trail:
        for trail in all_trail:
            liste_lonlat = get_trail_points(trail)
            if geodesic(points,liste_lonlat[0]).kilometers <= rayon_km:

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



def map_trail_by_point_and_mean_point(points, rayon_km, online = True):
    m = folium.Map(
        control_scale=True)
    all_points = []
    if online:
        all_trail = rq.get('https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist=0&max_dist=150').json()
    else:
        all_trail = rq.get('http://127.0.0.1:8000/docs/traces?min_dist=0&max_dist=150').json()

    folium.Marker(
        location=points,
        
    ).add_to(m)

    
    if all_trail:
        for trail in all_trail:
            liste_lonlat = get_trail_points(trail)
            mean_coordinates = mean_point(liste_lonlat)    
            if geodesic(points,mean_coordinates).kilometers <= rayon_km:

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




def map_trail_by_point_and_one_point(points, rayon_km, online = True):
    m = folium.Map(
        control_scale=True)
    all_points = []
    if online:
        all_trail = rq.get('https://api-gpx-l3miashs-2026.onrender.com/traces?min_dist=0&max_dist=150').json()
    else:
        all_trail = rq.get('http://127.0.0.1:8000/docs/traces?min_dist=0&max_dist=150').json()

    folium.Marker(
        location=points,
        
    ).add_to(m)

    
    if all_trail:
        for trail in all_trail:
            liste_lonlat = get_trail_points(trail)
            for pts in liste_lonlat:
                if geodesic(points,pts).kilometers <= rayon_km:

                    folium.PolyLine(
                        liste_lonlat,
                        tooltip=trail.name,
                        color="blue",
                        weight=3,
                    ).add_to(m)

                    all_points.extend(liste_lonlat)
                    break

        m.fit_bounds(all_points, padding=(30, 30))  ##centrage du zoom


    m.save("map.html")

    webbrowser.open("file://" + os.path.realpath("map.html"))


def mean_point(liste_lonlat):
    s1 = 0
    s2 = 0
    for point in liste_lonlat:
        s1+=point[0]
        s2+=point[1]
    return [s1/len(liste_lonlat),s2/len(liste_lonlat)] 



map_trail_by_point_and_mean_point([48.8566, 2.3522], 500 , False)



