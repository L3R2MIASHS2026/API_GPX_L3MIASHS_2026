import os
import requests
import folium
import webbrowser
import tempfile

#api_url = "http://127.0.0.1:8000"

class MapGenerator:
    def __init__(self,api_url="https://api-gpx-l3miashs-2026.onrender.com"):
        self.api_url = api_url
        print(f"Générateur initialisé ! Prêt à interroger l'API sur : {self.api_url}")


    def get_traces_from_api(self):
        route = f"{self.api_url}/traces"
        print(f"Interrogation de l'API sur : {route} ...")

        try:
            reponse = requests.get(route)
            reponse.raise_for_status()
            return reponse.json()


        except requests.exceptions.RequestException as erreur:
            print(f"Impossible de joindre l'API : {erreur}")
            print("💡 As-tu bien lancé ton serveur Uvicorn dans un autre terminal ?")
            return []

    def generate_global_map(self):
        traces = self.get_traces_from_api()
        if not traces:
            print("Aucune trace à afficher.")
            return
        # 1. On crée le fond de carte (centré sur la France)
        ma_carte = folium.Map(location=[46.204, 2.202], zoom_start=6)

        # 2. On boucle sur chaque trace pour dessiner son parcours
        for trace in traces:
            nom_trace = trace.get('name', 'Trace inconnue')

            if 'points' in trace and len(trace['points']) > 0:
                # On extrait toutes les coordonnées de la trace
                coordonnees = [[pt['latitude'], pt['longitude']] for pt in trace['points']]

                # On dessine la ligne sur la carte
                folium.PolyLine(
                    coordonnees,
                    color="blue",
                    weight=3,
                    tooltip=nom_trace  # Affiche le nom quand on passe la souris !
                ).add_to(ma_carte)
            else:
                print(f"La trace '{nom_trace}' n'a pas de points GPS dans ce JSON.")

        # 3. Sauvegarde temporaire et ouverture dans le navigateur
        self._save_and_open(ma_carte, "Carte Globale")

    def generate_single_map(self, trail_id):

        url = f"{self.api_url}/traces/{trail_id}"
        print(f"Récupération de la trace n°{trail_id} sur {url}...")

        try:
            response = requests.get(url)
            if response.status_code == 404:
                print(f"La trace avec l'ID {trail_id} est introuvable.")
                return
            response.raise_for_status()
            trace = response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à l'API : {e}")
            return

        # On vérifie qu'on a bien des points GPS
        if 'points' not in trace or len(trace['points']) == 0:
            print(f"La trace '{trace.get('name')}' n'a pas de points GPS.")
            return

        # 1. On récupère le tout premier point pour centrer la carte exactement au bon endroit
        premier_point = trace['points'][0]
        centre_carte = [premier_point['latitude'], premier_point['longitude']]

        # 2. On crée la carte avec un gros niveau de zoom (13)
        ma_carte = folium.Map(location=centre_carte, zoom_start=13)

        # 3. On dessine la ligne (en rouge cette fois pour changer !)
        coordonnees = [[pt['latitude'], pt['longitude']] for pt in trace['points']]
        folium.PolyLine(
            coordonnees,
            color="red",
            weight=4,
            tooltip=trace.get('name')
        ).add_to(ma_carte)

        # 4. On sauvegarde et on ouvre
        self._save_and_open(ma_carte, f"Trace {trace.get('name')}")







    def _save_and_open(self, carte_folium, nom_affichage):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp_file:
            chemin_fichier = tmp_file.name
            carte_folium.save(chemin_fichier)

        print(f"Terminé ! Ouverture du navigateur pour : {nom_affichage}")
        webbrowser.open('file://' + chemin_fichier)




if __name__ == "__main__":
    mon_generateur = MapGenerator()

  #  print("\n--- TEST 1 : CARTE GLOBALE ---")
 #   mon_generateur.generate_global_map()

    print("\n--- TEST 2 : CARTE INDIVIDUELLE ---")

    mon_generateur.generate_single_map(trail_id=1)