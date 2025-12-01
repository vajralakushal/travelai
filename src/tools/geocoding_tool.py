import requests

class GeocodingTool:
    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.photon_url = "https://photon.komoot.io/api/"
    
    def get_coordinates(self, location: str):
        """
        Get latitude and longitude for a location with fallback services
        """
        # Try Photon first (faster, no rate limits)
        result = self._try_photon(location)
        if result and "error" not in result:
            return result
        
        # Fallback to Nominatim
        result = self._try_nominatim(location)
        if result and "error" not in result:
            return result
        
        return {"error": "Could not geocode location"}
    
    def _try_photon(self, location: str):
        """Try Photon geocoding service (Komoot)"""
        try:
            params = {"q": location, "limit": 1}
            response = requests.get(self.photon_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data.get("features"):
                coords = data["features"][0]["geometry"]["coordinates"]
                props = data["features"][0]["properties"]
                return {
                    "lat": coords[1],  # Photon returns [lon, lat]
                    "lon": coords[0],
                    "display_name": props.get("name", location)
                }
        except Exception as e:
            print(f"[DEBUG] Photon failed: {e}")
            return None
    
    def _try_nominatim(self, location: str):
        """Try Nominatim geocoding service (OpenStreetMap)"""
        try:
            params = {"q": location, "format": "json", "limit": 1}
            headers = {"User-Agent": "WanderAI/1.0 (travel-planner-app)"}
            response = requests.get(self.nominatim_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if data:
                return {
                    "lat": float(data[0]["lat"]),
                    "lon": float(data[0]["lon"]),
                    "display_name": data[0]["display_name"]
                }
        except Exception as e:
            print(f"[DEBUG] Nominatim failed: {e}")
            return None