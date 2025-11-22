"""Emergency Service Module for Hospital Finder
Provides geolocation-based hospital finding functionality
"""

import os
import requests
from typing import List, Dict, Optional, Tuple
from math import radians, sin, cos, sqrt, atan2
import logging

logger = logging.getLogger(__name__)

class EmergencyService:
    """Service for finding nearby hospitals and emergency facilities"""
    
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')
        self.use_google_maps = bool(self.google_api_key)
        
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        lat1_rad, lon1_rad = radians(lat1), radians(lon1)
        lat2_rad, lon2_rad = radians(lat2), radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat/2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        return R * c
    
    def find_nearby_hospitals_google(self, latitude: float, longitude: float, 
                                     radius: int = 5000) -> List[Dict]:
        """Find nearby hospitals using Google Places API"""
        if not self.google_api_key:
            logger.warning("Google Maps API key not configured")
            return []
            
        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{latitude},{longitude}",
                'radius': radius,
                'type': 'hospital',
                'key': self.google_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            hospitals = []
            
            for place in data.get('results', []):
                hospital_lat = place['geometry']['location']['lat']
                hospital_lon = place['geometry']['location']['lng']
                distance = self.calculate_distance(latitude, longitude, 
                                                   hospital_lat, hospital_lon)
                
                hospitals.append({
                    'name': place.get('name', 'Unknown Hospital'),
                    'address': place.get('vicinity', 'Address not available'),
                    'latitude': hospital_lat,
                    'longitude': hospital_lon,
                    'distance_km': round(distance, 2),
                    'rating': place.get('rating'),
                    'is_open': place.get('opening_hours', {}).get('open_now'),
                    'place_id': place.get('place_id')
                })
            
            # Sort by distance
            hospitals.sort(key=lambda x: x['distance_km'])
            return hospitals
            
        except Exception as e:
            logger.error(f"Error fetching hospitals from Google Maps: {e}")
            return []
    
    def find_nearby_hospitals_osm(self, latitude: float, longitude: float, 
                                  radius_km: float = 5.0) -> List[Dict]:
        """Find nearby hospitals using OpenStreetMap Overpass API (free alternative)"""
        try:
            # Convert radius to meters for Overpass API
            radius_m = int(radius_km * 1000)
            
            overpass_url = "http://overpass-api.de/api/interpreter"
            overpass_query = f"""
            [out:json];
            (
              node["amenity"="hospital"](around:{radius_m},{latitude},{longitude});
              way["amenity"="hospital"](around:{radius_m},{latitude},{longitude});
            );
            out center;
            """
            
            response = requests.post(overpass_url, data={'data': overpass_query}, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            hospitals = []
            
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                
                # Get coordinates
                if element['type'] == 'node':
                    hosp_lat = element['lat']
                    hosp_lon = element['lon']
                elif 'center' in element:
                    hosp_lat = element['center']['lat']
                    hosp_lon = element['center']['lon']
                else:
                    continue
                
                distance = self.calculate_distance(latitude, longitude, hosp_lat, hosp_lon)
                
                hospitals.append({
                    'name': tags.get('name', 'Hospital'),
                    'address': tags.get('addr:full', tags.get('addr:street', 'Address not available')),
                    'latitude': hosp_lat,
                    'longitude': hosp_lon,
                    'distance_km': round(distance, 2),
                    'phone': tags.get('phone', tags.get('contact:phone')),
                    'emergency': tags.get('emergency') == 'yes',
                    'operator': tags.get('operator')
                })
            
            # Sort by distance
            hospitals.sort(key=lambda x: x['distance_km'])
            return hospitals
            
        except Exception as e:
            logger.error(f"Error fetching hospitals from OpenStreetMap: {e}")
            return []
    
    def get_nearby_hospitals(self, latitude: float, longitude: float, 
                            radius_km: float = 5.0, max_results: int = 10) -> List[Dict]:
        """Get nearby hospitals using available API (Google Maps or OpenStreetMap)"""
        
        # Try Google Maps first if API key is available
        if self.use_google_maps:
            hospitals = self.find_nearby_hospitals_google(latitude, longitude, 
                                                         int(radius_km * 1000))
            if hospitals:
                return hospitals[:max_results]
        
        # Fallback to OpenStreetMap
        hospitals = self.find_nearby_hospitals_osm(latitude, longitude, radius_km)
        return hospitals[:max_results]
    
    def get_emergency_contacts(self, country: str = 'IN') -> Dict[str, str]:
        """Get emergency contact numbers for different countries"""
        emergency_numbers = {
            'IN': {
                'ambulance': '108',
                'police': '100',
                'fire': '101',
                'disaster': '108',
                'women_helpline': '1091',
                'child_helpline': '1098'
            },
            'US': {
                'emergency': '911',
                'poison_control': '1-800-222-1222'
            },
            'UK': {
                'emergency': '999',
                'non_emergency': '111'
            }
        }
        return emergency_numbers.get(country, emergency_numbers['IN'])
    
    def format_hospital_response(self, hospitals: List[Dict], 
                                user_location: Tuple[float, float]) -> str:
        """Format hospital list into a readable message"""
        if not hospitals:
            return ("⚠️ No hospitals found nearby. Please call emergency services:\n"
                   "🚑 Ambulance: 108\n📞 Police: 100\n🔥 Fire: 101")
        
        response = f"🏥 **Found {len(hospitals)} nearby hospitals:**\n\n"
        
        for i, hospital in enumerate(hospitals, 1):
            response += f"{i}. **{hospital['name']}**\n"
            response += f"   📍 {hospital['address']}\n"
            response += f"   📏 Distance: {hospital['distance_km']} km\n"
            
            if hospital.get('phone'):
                response += f"   📞 Phone: {hospital['phone']}\n"
            
            if hospital.get('rating'):
                response += f"   ⭐ Rating: {hospital['rating']}/5\n"
            
            if hospital.get('is_open') is not None:
                status = "🟢 Open Now" if hospital['is_open'] else "🔴 Closed"
                response += f"   {status}\n"
            
            if hospital.get('emergency'):
                response += f"   🚨 Emergency Services Available\n"
            
            response += "\n"
        
        response += "\n⚠️ **Emergency Contacts:**\n🚑 Ambulance: 108\n📞 Police: 100\n🔥 Fire: 101"
        
        return response


# Singleton instance
_emergency_service = None

def get_emergency_service() -> EmergencyService:
    """Get or create singleton emergency service instance"""
    global _emergency_service
    if _emergency_service is None:
        _emergency_service = EmergencyService()
    return _emergency_service
