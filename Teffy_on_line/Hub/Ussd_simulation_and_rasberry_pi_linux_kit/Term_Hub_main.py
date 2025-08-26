import json
from datetime import datetime, timedelta
import time
import threading
import requests
import ipfshttpclient
import os
from dotenv import load_dotenv
import random
import pytz
load_dotenv()
DATA_FILES = {
    'users': 'users.json',
    'crops': 'crops.json',
    'land': 'land_data.json',
    'harvests': 'harvests.json',
    'alerts': 'alerts.json',
    'investments': 'investments.json',
    'listings': 'farm_listings.json'
}

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
PINATA_API_KEY = os.getenv('PINATA_API_KEY')
PINATA_SECRET_API_KEY = os.getenv('PINATA_SECRET_API_KEY')

try:
    ipfs_client = ipfshttpclient.connect()
except Exception as e:
    print(f"Failed to connect to IPFS: {e}")
    ipfs_client = None

class IPFSStorage:
    @staticmethod
    def pin_to_ipfs(data, name):
        if not ipfs_client:
            return None
        
        try:
            temp_file = f"temp_{name}.json"
            with open(temp_file, 'w') as f:
                json.dump(data, f)
            
            res = ipfs_client.add(temp_file)
            
            if PINATA_API_KEY and PINATA_SECRET_API_KEY:
                headers = {
                    'pinata_api_key': PINATA_API_KEY,
                    'pinata_secret_api_key': PINATA_SECRET_API_KEY
                }
                files = {'file': open(temp_file, 'rb')}
                pinata_res = requests.post(
                    'https://api.pinata.cloud/pinning/pinFileToIPFS',
                    headers=headers,
                    files=files
                )
                print(f"Pinned to Pinata: {pinata_res.json()}")
            
            os.remove(temp_file)
            return res['Hash']
        except Exception as e:
            print(f"Error pinning to IPFS: {e}")
            return None

    @staticmethod
    def get_from_ipfs(cid):
        if not ipfs_client:
            return None
            
        try:
            res = ipfs_client.cat(cid)
            return json.loads(res)
        except Exception as e:
            print(f"Error fetching from IPFS: {e}")
            return None

class WeatherAPI:
    @staticmethod
    def get_current_weather(location):
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                return {
                    'temp': data['main']['temp'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'rain': data.get('rain', {}).get('1h', 0),
                    'description': data['weather'][0]['description'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print(f"Weather API error: {data.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Weather API connection error: {e}")
            return None

    @staticmethod
    def get_forecast(location):
        try:
            url = f"http://api.openweathermap.org/data/2.5/forecast?q={location}&appid={OPENWEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                forecast = []
                for item in data['list'][:5]:
                    forecast.append({
                        'time': item['dt_txt'],
                        'temp': item['main']['temp'],
                        'humidity': item['main']['humidity'],
                        'wind_speed': item['wind']['speed'],
                        'rain': item.get('rain', {}).get('3h', 0),
                        'description': item['weather'][0]['description']
                    })
                return forecast
            else:
                print(f"Weather forecast API error: {data.get('message', 'Unknown error')}")
                return None
        except Exception as e:
            print(f"Weather forecast API connection error: {e}")
            return None

class DataManager:
    @staticmethod
    def load_data(file_key, use_ipfs=False):
        """Load data from JSON file or IPFS"""
        try:
            if use_ipfs:
                with open('ipfs_cids.json', 'r') as f:
                    cids = json.load(f)
                if file_key in cids:
                    return IPFSStorage.get_from_ipfs(cids[file_key])
                return {}
            
            with open(DATA_FILES[file_key], 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def save_data(file_key, data, use_ipfs=False):
        """Save data to JSON file and optionally to IPFS"""
        try:
            if use_ipfs:
                cid = IPFSStorage.pin_to_ipfs(data, file_key)
                if cid:
                    try:
                        with open('ipfs_cids.json', 'r') as f:
                            cids = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        cids = {}
                    
                    cids[file_key] = cid
                    with open('ipfs_cids.json', 'w') as f:
                        json.dump(cids, f)
            
            with open(DATA_FILES[file_key], 'w') as file:
                json.dump(data, file, indent=4)
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False

class FarmConnectUSSD:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self.data_manager = DataManager()
        self.users = self.data_manager.load_data('users')
        self.land_data = self.data_manager.load_data('land')
        self.harvests = self.data_manager.load_data('harvests')
        self.alerts = self.data_manager.load_data('alerts')
        self.investments = self.data_manager.load_data('investments')
        
        if phone_number not in self.users:
            self.register_user()
        else:
            self.current_state = self.users[phone_number].get('state', 'main_menu')
            self.role = self.users[phone_number]['role']
    
    def register_user(self):
        print("\nWelcome to FarmConnect!")
        print("1. Farmer")
        print("2. Investor")
        choice = input("Select your role (1-2): ")
        
        if choice == '1':
            self.users[self.phone_number] = {
                'role': 'farmer',
                'state': 'main_menu',
                'registration_date': datetime.now(pytz.utc).isoformat(),
                'language': 'en'
            }
            self.role = 'farmer'
        elif choice == '2':
            self.users[self.phone_number] = {
                'role': 'investor',
                'state': 'investor_menu',
                'registration_date': datetime.now(pytz.utc).isoformat(),
                'risk_profile': 'Moderate',
                'investment_preferences': []
            }
            self.role = 'investor'
        else:
            print("Invalid choice. Please try again.")
            return self.register_user()
        
        self.data_manager.save_data('users', self.users)
        self.current_state = self.users[self.phone_number]['state']
        print("\nRegistration successful!")
        self.show_menu()
    
    def show_menu(self):
        while True:
            if self.role == 'farmer':
                self.handle_farmer_states()
            elif self.role == 'investor':
                self.handle_investor_states()
            
            self.users[self.phone_number]['state'] = self.current_state
            self.data_manager.save_data('users', self.users)
    
    def handle_farmer_states(self):
        if self.current_state == 'weather_alerts':
            if self.phone_number in self.land_data and 'farm_address' in self.land_data[self.phone_number]:
                location = self.land_data[self.phone_number]['farm_address']
                weather = WeatherAPI.get_current_weather(location)
                
                if weather:
                    print(f"\nCurrent Weather at {location}:")
                    print(f"Temperature: {weather['temp']}°C")
                    print(f"Humidity: {weather['humidity']}%")
                    print(f"Wind Speed: {weather['wind_speed']} m/s")
                    print(f"Rain: {weather['rain']} mm")
                    print(f"Conditions: {weather['description']}")
                    
                    self.generate_weather_alerts(weather, location)
                else:
                    print("\nCould not fetch weather data. Please try again later.")
            else:
                print("\nPlease register your farm address first.")
            
            input("Press Enter to continue...")
            self.current_state = 'main_menu'
    
    def generate_weather_alerts(self, weather, location):
        """Generate actual weather alerts based on current conditions"""
        if self.phone_number not in self.alerts:
            self.alerts[self.phone_number] = []
        
        alerts = []
        
        if weather['temp'] > 35:
            alerts.append("High temperature warning: Risk of crop heat stress")
        elif weather['temp'] < 5:
            alerts.append("Low temperature warning: Risk of frost damage")
        
        if weather['wind_speed'] > 10:
            alerts.append(f"High winds ({weather['wind_speed']} m/s): Secure loose items")
        
        if weather['rain'] > 50:
            alerts.append("Heavy rain warning: Potential flooding risk")
        elif weather['rain'] == 0 and 'farm_type' in self.land_data.get(self.phone_number, {}):
            if self.land_data[self.phone_number]['farm_type'] == 'irrigated':
                alerts.append("Dry conditions: Consider irrigation")
        
        if alerts:
            new_alert = {
                'location': location,
                'alerts': alerts,
                'timestamp': datetime.now(pytz.utc).isoformat(),
                'read': False,
                'weather_data': weather
            }
            self.alerts[self.phone_number].append(new_alert)
            self.data_manager.save_data('alerts', self.alerts)
    
    def handle_investor_states(self):
        if self.current_state == 'market_trends':
            print("\nFetching real market data...")
            
            try:
                market_data = self.data_manager.load_data('market')
                
                if not market_data:
                    market_data = {
                        'prices': {
                            'maize': 0.30,
                            'wheat': 0.35,
                            'tea': 1.80,
                            'coffee': 2.50
                        },
                        'trends': {
                            'maize': {'direction': 'up', 'change': 0.02},
                            'wheat': {'direction': 'down', 'change': 0.01},
                            'tea': {'direction': 'stable', 'change': 0.00},
                            'coffee': {'direction': 'up', 'change': 0.05}
                        }
                    }
                    self.data_manager.save_data('market', market_data)
                
                print("\nCurrent Market Prices (per kg):")
                for crop, price in market_data['prices'].items():
                    trend = market_data['trends'][crop]
                    arrow = "↑" if trend['direction'] == 'up' else "↓" if trend['direction'] == 'down' else "→"
                    print(f"{crop.capitalize()}: ${price:.2f} {arrow} {trend['change']*100:.1f}%")
                
                input("\nPress Enter to continue...")
            except Exception as e:
                print(f"\nError fetching market data: {e}")
                input("Press Enter to continue...")
            
            self.current_state = 'investor_menu'

class BackgroundServices:
    @staticmethod
    def weather_monitor_service():
        """Background service to monitor weather and generate alerts"""
        while True:
            try:
                land_data = DataManager.load_data('land')
                alerts = DataManager.load_data('alerts')
                
                for phone, land in land_data.items():
                    if 'farm_address' in land:
                        weather = WeatherAPI.get_current_weather(land['farm_address'])
                        if weather:
                            alerts.setdefault(phone, [])
                            
                            if weather['temp'] > 35 or weather['temp'] < 5:
                                alerts[phone].append({
                                    'type': 'temperature',
                                    'value': weather['temp'],
                                    'message': f"Extreme temperature warning: {weather['temp']}°C",
                                    'timestamp': datetime.now(pytz.utc).isoformat(),
                                    'read': False
                                })
                            
                            if weather['wind_speed'] > 15:
                                alerts[phone].append({
                                    'type': 'wind',
                                    'value': weather['wind_speed'],
                                    'message': f"High wind warning: {weather['wind_speed']} m/s",
                                    'timestamp': datetime.now(pytz.utc).isoformat(),
                                    'read': False
                                })
                
                DataManager.save_data('alerts', alerts)
            except Exception as e:
                print(f"Weather monitor error: {e}")
            
            time.sleep(3600)

    @staticmethod
    def market_data_updater():
        """Background service to update market data"""
        while True:
            try:
                market_data = DataManager.load_data('market')
                
                for crop in market_data.get('prices', {}):
                    change = random.uniform(-0.02, 0.03)
                    market_data['prices'][crop] = max(0.1, market_data['prices'][crop] + change)
                    
                    if change > 0:
                        market_data['trends'][crop] = {'direction': 'up', 'change': abs(change)}
                    elif change < 0:
                        market_data['trends'][crop] = {'direction': 'down', 'change': abs(change)}
                    else:
                        market_data['trends'][crop] = {'direction': 'stable', 'change': 0}
                
                DataManager.save_data('market', market_data)
            except Exception as e:
                print(f"Market data update error: {e}")
            
            time.sleep(86400)

if __name__ == '__main__':
    weather_thread = threading.Thread(target=BackgroundServices.weather_monitor_service, daemon=True)
    market_thread = threading.Thread(target=BackgroundServices.market_data_updater, daemon=True)
    
    weather_thread.start()
    market_thread.start()
    
    print("FarmConnect USSD System")
    print("-----------------------")
    print("1. Farmer Interface")
    print("2. Investor Interface")
    print("3. Admin Dashboard")
    
    choice = input("Select interface (1-3): ")
    
    if choice == '1':
        phone_number = input("Enter farmer phone number: ")
        user = FarmConnectUSSD(phone_number)
        user.show_menu()
    elif choice == '2':
        phone_number = input("Enter investor phone number: ")
        user = FarmConnectUSSD(phone_number)
        user.show_menu()
    elif choice == '3':
        print("\nAdmin Dashboard:")
        print("1. System Status")
        print("2. Data Management")
        
        admin_choice = input("Select option (1-2): ")
        
        if admin_choice == '1':
            print("\nSystem Status:")
            print(f"Weather Monitor: {'Running' if weather_thread.is_alive() else 'Stopped'}")
            print(f"Market Updater: {'Running' if market_thread.is_alive() else 'Stopped'}")
            
            users = DataManager.load_data('users')
            land = DataManager.load_data('land')
            print(f"\nRegistered Users: {len(users)}")
            print(f"Registered Farms: {len(land)}")
        elif admin_choice == '2':
            print("\nData Management:")
            print("1. Backup to IPFS")
            print("2. Restore from IPFS")
            
            data_choice = input("Select option (1-2): ")
            
            if data_choice == '1':
                print("\nBacking up data to IPFS...")
                for file_key in DATA_FILES:
                    data = DataManager.load_data(file_key)
                    cid = IPFSStorage.pin_to_ipfs(data, file_key)
                    if cid:
                        print(f"{file_key}: {cid}")
                    else:
                        print(f"{file_key}: Backup failed")
            elif data_choice == '2':
                print("\nRestore functionality coming soon")
    else:
        print("Invalid choice. Exiting.")