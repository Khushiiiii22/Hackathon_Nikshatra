/**
 * Emergency Service for Frontend
 * Handles geolocation and hospital finding on the client side
 */

export interface Hospital {
  name: string;
  address: string;
  latitude: number;
  longitude: number;
  distance_km: number;
  phone?: string;
  rating?: number;
  is_open?: boolean;
  emergency?: boolean;
}

export interface EmergencyContacts {
  ambulance: string;
  police: string;
  fire: string;
  [key: string]: string;
}

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

export class EmergencyService {
  /**
   * Get user's current location using browser geolocation API
   */
  async getUserLocation(): Promise<{ latitude: number; longitude: number }> {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by your browser'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          });
        },
        (error) => {
          let errorMessage = 'Unable to retrieve location';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location permission denied. Please enable location access.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information unavailable.';
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timed out.';
              break;
          }
          reject(new Error(errorMessage));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    });
  }

  /**
   * Find nearby hospitals using backend API
   */
  async findNearbyHospitals(
    latitude: number,
    longitude: number,
    radiusKm: number = 5
  ): Promise<Hospital[]> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/emergency/hospitals?lat=${latitude}&lon=${longitude}&radius=${radiusKm}`
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.hospitals || [];
    } catch (error) {
      console.error('Error fetching nearby hospitals:', error);
      throw error;
    }
  }

  /**
   * Get emergency contact numbers
   */
  async getEmergencyContacts(country: string = 'IN'): Promise<EmergencyContacts> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/emergency/contacts?country=${country}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.contacts || this.getDefaultContacts();
    } catch (error) {
      console.error('Error fetching emergency contacts:', error);
      return this.getDefaultContacts();
    }
  }

  /**
   * Get default emergency contacts for India
   */
  private getDefaultContacts(): EmergencyContacts {
    return {
      ambulance: '108',
      police: '100',
      fire: '101',
      disaster: '108',
      women_helpline: '1091',
      child_helpline: '1098',
    };
  }

  /**
   * Open phone dialer with emergency number
   */
  callEmergency(phoneNumber: string): void {
    window.location.href = `tel:${phoneNumber}`;
  }

  /**
   * Open maps app with hospital directions
   */
  openMapsDirections(hospital: Hospital): void {
    const url = `https://www.google.com/maps/dir/?api=1&destination=${hospital.latitude},${hospital.longitude}`;
    window.open(url, '_blank');
  }

  /**
   * Format hospital data for display
   */
  formatHospitalInfo(hospital: Hospital): string {
    let info = `${hospital.name}\n`;
    info += `📍 ${hospital.address}\n`;
    info += `📏 Distance: ${hospital.distance_km} km\n`;

    if (hospital.phone) {
      info += `📞 ${hospital.phone}\n`;
    }

    if (hospital.rating) {
      info += `⭐ Rating: ${hospital.rating}/5\n`;
    }

    if (hospital.is_open !== undefined) {
      info += hospital.is_open ? '🟢 Open Now\n' : '🔴 Closed\n';
    }

    if (hospital.emergency) {
      info += '🚨 Emergency Services Available\n';
    }

    return info;
  }
}

// Export singleton instance
export const emergencyService = new EmergencyService();
