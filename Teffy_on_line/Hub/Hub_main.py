import json
import requests
from flask import Flask, request
from datetime import datetime, timedelta
import threading
import time

app = Flask(__name__)

WEATHER_API_KEY = "*"
WEATHER_API_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_API_URL = "http://api.openweathermap.org/data/2.5/forecast"

CROP_SENSITIVITY = {
    "maize": {"min_temp": 10, "max_temp": 35, "max_wind": 30, "min_rain": 20, "max_rain": 150},
    "wheat": {"min_temp": 0, "max_temp": 30, "max_wind": 25, "min_rain": 15, "max_rain": 100},
    "tea": {"min_temp": 15, "max_temp": 30, "max_wind": 20, "min_rain": 50, "max_rain": 200},
    "coffee": {"min_temp": 15, "max_temp": 28, "max_wind": 25, "min     _rain": 60, "max_rain": 250},
}
def load_investments():
    try:
        with open("investments.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_investments(investments):
    with open("investments.json", "w") as file:
        json.dump(investments, file, indent=4)

def load_farm_listings():
    try:
        with open("farm_listings.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_farm_listings(listings):
    with open("farm_listings.json", "w") as file:
        json.dump(listings, file, indent=4)
def load_users():
    try:
        with open("users.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file, indent=4)

def load_crops():
    try:
        with open("crops.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_crops(crops):
    with open("crops.json", "w") as file:
        json.dump(crops, file, indent=4)

def load_land_data():
    try:
        with open("land_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_land_data(data):
    with open("land_data.json", "w") as file:
        json.dump(data, file, indent=4)

def load_harvests():
    try:
        with open("harvests.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_harvests(harvests):
    with open("harvests.json", "w") as file:
        json.dump(harvests, file, indent=4)

def load_alerts():
    try:
        with open("alerts.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_alerts(alerts):
    with open("alerts.json", "w") as file:
        json.dump(alerts, file, indent=4)

def get_weather_data(location):
    """Fetch current weather data for a location"""
    try:
        params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(WEATHER_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def get_weather_forecast(location):
    """Fetch 5-day weather forecast"""
    try:
        params = {
            'q': location,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        response = requests.get(FORECAST_API_URL, params=params)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Weather forecast error: {e}")
        return None

def check_weather_threats(weather_data, crops):
    """Check if weather conditions pose threats to specific crops"""
    alerts = []
    if not weather_data or not crops:
        return alerts
    
    main_weather = weather_data.get('weather', [{}])[0].get('main', '').lower()
    temp = weather_data.get('main', {}).get('temp', 0)
    wind_speed = weather_data.get('wind', {}).get('speed', 0)
    rain = weather_data.get('rain', {}).get('1h', 0)
    
    for crop in crops:
        crop_type = crop.get('crop_type', '').lower()
        if crop_type not in CROP_SENSITIVITY:
            continue
            
        thresholds = CROP_SENSITIVITY[crop_type]
        crop_alerts = []
        
        if temp < thresholds['min_temp']:
            crop_alerts.append(f"Low temperature alert: {temp}°C (min {thresholds['min_temp']}°C for {crop_type})")
        if temp > thresholds['max_temp']:
            crop_alerts.append(f"High temperature alert: {temp}°C (max {thresholds['max_temp']}°C for {crop_type})")
        if wind_speed > thresholds['max_wind']:
            crop_alerts.append(f"High wind alert: {wind_speed} km/h (max {thresholds['max_wind']} km/h for {crop_type})")
        if rain < thresholds['min_rain']:
            crop_alerts.append(f"Drought alert: Only {rain}mm rain (min {thresholds['min_rain']}mm needed for {crop_type})")
        if rain > thresholds['max_rain']:
            crop_alerts.append(f"Flood alert: {rain}mm rain (max {thresholds['max_rain']}mm for {crop_type})")
        
        if crop_alerts:
            alerts.append({
                'crop': crop_type,
                'alerts': crop_alerts,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
    
    return alerts

def check_all_farms():
    """Background task to check all farms for weather threats"""
    while True:
        try:
            land_data = load_land_data()
            harvests = load_harvests()
            alerts = load_alerts()
            
            for phone, land in land_data.items():
                if 'farm_address' not in land:
                    continue
                    
                current_crops = []
                if phone in harvests:
                    recent_harvests = sorted(harvests[phone], 
                                           key=lambda x: x.get('date', ''),
                                           reverse=True)[:3]
                    current_crops = [{'crop_type': h['crop_type']} for h in recent_harvests]
                
                if not current_crops:
                    continue
                
                weather = get_weather_data(land['farm_address'])
                if not weather:
                    continue
                
                crop_alerts = check_weather_threats(weather, current_crops)
                if crop_alerts:
                    if phone not in alerts:
                        alerts[phone] = []
                    alerts[phone].extend(crop_alerts)
                    save_alerts(alerts)
                    
        except Exception as e:
            print(f"Error in weather check: {e}")
        
        time.sleep(6 * 60 * 60)

weather_thread = threading.Thread(target=check_all_farms, daemon=True)
weather_thread.start()


@app.route('/ussd', methods=['POST'])
def ussd():
    session_id = request.values.get("sessionId", "")
    phone_number = request.values.get("phoneNumber", "")
    text = request.values.get("text", "")

    users = load_users()
    crops = load_crops()
    land_data = load_land_data()
    harvests = load_harvests()
    alerts = load_alerts()

    if phone_number not in users:
        pass
    else:
        user_role = users[phone_number]["role"]
        state = users[phone_number].get("state", "main_menu")

        if user_role == "farmer":
            if state == "register_land":
                if text == "":
                    response = "CON Please enter your farm's name:"
                else:
                    land_data[phone_number] = {"farm_name": text}
                    users[phone_number]["state"] = "farm_type"
                    save_users(users)
                    response = "CON What type of farm is this? (e.g., mixed, organic)"
            elif state == "farm_type":
                land_data[phone_number]["farm_type"] = text
                users[phone_number]["state"] = "farming_practice"
                save_users(users)
                response = "CON What farming practices do you use? (e.g., organic, conventional)"
            elif state == "farming_practice":
                land_data[phone_number]["farming_practice"] = text
                users[phone_number]["state"] = "farm_address"
                save_users(users)
                response = "CON Please provide the farm's address:"
            elif state == "farm_address":
                land_data[phone_number]["farm_address"] = text
                users[phone_number]["state"] = "elevation"
                save_users(users)
                response = "CON What is the elevation of your farm?"
            elif state == "elevation":
                land_data[phone_number]["elevation"] = text
                users[phone_number]["state"] = "access_roads"
                save_users(users)
                response = "CON Please describe the access roads to your farm:"
            elif state == "access_roads":
                land_data[phone_number]["access_roads"] = text
                users[phone_number]["state"] = "collateral"
                save_users(users)
                response = "CON What assets are pledged as collateral for your farm?"
            elif state == "collateral":
                land_data[phone_number]["collateral"] = text
                users[phone_number]["state"] = "certifications"
                save_users(users)
                response = "CON Provide links to any relevant certifications:"
            elif state == "certifications":
                land_data[phone_number]["certifications"] = text
                users[phone_number]["state"] = "farm_images"
                save_users(users)
                response = "CON Provide links to images of your farm (e.g., aerial photos):"
            elif state == "farm_images":
                land_data[phone_number]["farm_images"] = text
                users[phone_number]["state"] = "contact_email"
                save_users(users)
                response = "CON Please provide your contact email:"
            elif state == "contact_email":
                land_data[phone_number]["contact_email"] = text
                users[phone_number]["state"] = "contact_phone"
                save_users(users)
                response = "CON Please provide your contact phone number:"
            elif state == "contact_phone":
                land_data[phone_number]["contact_phone"] = text
                users[phone_number]["state"] = "current_revenue"
                save_users(users)
                response = "CON What is your farm's current revenue?"
            elif state == "current_revenue":
                land_data[phone_number]["current_revenue"] = text
                users[phone_number]["state"] = "fund_amount"
                save_users(users)
                response = "CON How much funding do you need for this farm?"
            elif state == "fund_amount":
                land_data[phone_number]["fund_amount"] = text
                users[phone_number]["state"] = "main_menu"
                save_land_data(land_data)
                save_users(users)
                response = "END Your farm has been successfully registered!"
            elif state == "main_menu":
                if text == "":
                    response = "CON Farmer Menu:\n"
                    response += "1. My Lands\n"
                    response += "2. Profile\n"
                    response += "3. Register New Land\n"
                    response += "4. Harvest Tracking"
                elif text == "1":
                    if phone_number in land_data:
                        land = land_data[phone_number]
                        response = "END My Land Info:\n"
                        response += f"Name: {land.get('farm_name', 'N/A')}\n"
                        response += f"Type: {land.get('farm_type', 'N/A')}\n"
                        response += f"Practice: {land.get('farming_practice', 'N/A')}\n"
                        response += f"Address: {land.get('farm_address', 'N/A')}\n"
                        response += f"Elevation: {land.get('elevation', 'N/A')}\n"
                        response += f"Revenue: {land.get('current_revenue', 'N/A')}\n"
                        response += f"Funding: {land.get('fund_amount', 'N/A')}"
                    else:
                        response = "END You don't have any registered land yet."
                elif text == "2":
                    users[phone_number]["state"] = "profile_menu"
                    save_users(users)
                    response = "CON Profile:\n1. View Profile\n2. Edit Profile"
                elif text == "3":
                    users[phone_number]["state"] = "register_land"
                    save_users(users)
                    response = "CON Enter your farm's name:"
                elif text == "4":
                    users[phone_number]["state"] = "harvest_menu"
                    save_users(users)
                    response = "CON Harvest Tracking:\n1. Record New Harvest\n2. View Past Harvests"
                else:
                    response = "END Invalid choice."
            
            elif state == "main_menu":
                if text == "":
                    unread_alerts = 0
                    if phone_number in alerts:
                        unread_alerts = len([a for a in alerts[phone_number] if not a.get('read', False)])
                    
                    response = "CON Farmer Menu:\n"
                    response += "1. My Lands\n"
                    response += "2. Profile\n"
                    response += "3. Register New Land\n"
                    response += "4. Harvest Tracking\n"
                    response += f"5. Weather Alerts ({unread_alerts} new)"
                elif text == "1":
                    pass
                elif text == "5":
                    users[phone_number]["state"] = "weather_alerts"
                    save_users(users)
                    response = "CON Weather Alerts:\n1. View Alerts\n2. Weather Forecast\n3. Crop Advice"
            
            elif state == "weather_alerts":
                if text == "":
                    response = "CON Weather Alerts:\n1. View Alerts\n2. Weather Forecast\n3. Crop Advice"
                elif text == "1":
                    if phone_number in alerts and alerts[phone_number]:
                        users[phone_number]["state"] = "view_alerts"
                        save_users(users)
                        
                        for alert in alerts[phone_number]:
                            alert['read'] = True
                        save_alerts(alerts)
                        
                        response = "CON Latest Alerts:\n"
                        for i, alert in enumerate(alerts[phone_number][-3:], 1):
                            crop = alert.get('crop', 'unknown')
                            first_msg = alert['alerts'][0] if alert['alerts'] else "No details"
                            response += f"{i}. {crop}: {first_msg[:30]}...\n"
                        response += "Select alert for details (1-3) or 0 to go back"
                    else:
                        response = "END No weather alerts at this time."
                elif text == "2":
                    if phone_number in land_data and 'farm_address' in land_data[phone_number]:
                        forecast = get_weather_forecast(land_data[phone_number]['farm_address'])
                        if forecast:
                            response = "END Weather Forecast:\n"
                            for day in forecast['list'][:3]:
                                date = datetime.fromtimestamp(day['dt']).strftime('%a %H:%M')
                                temp = day['main']['temp']
                                desc = day['weather'][0]['description']
                                response += f"{date}: {temp}°C, {desc}\n"
                        else:
                            response = "END Could not fetch forecast. Try again later."
                    else:
                        response = "END Please register your farm address first."
                elif text == "3":
                    users[phone_number]["state"] = "crop_advice"
                    save_users(users)
                    response = "CON Select crop for advice:\n"
                    if phone_number in harvests:
                        unique_crops = list(set(h['crop_type'] for h in harvests[phone_number]))
                        for i, crop in enumerate(unique_crops[:5], 1):
                            response += f"{i}. {crop}\n"
                    else:
                        response = "END No crops registered yet."
                else:
                    response = "END Invalid input."
            
            elif state == "view_alerts":
                if text == "0":
                    users[phone_number]["state"] = "weather_alerts"
                    save_users(users)
                    response = "CON Weather Alerts:\n1. View Alerts\n2. Weather Forecast\n3. Crop Advice"
                elif text.isdigit() and 1 <= int(text) <= 3:
                    alert_index = int(text) - 1
                    if phone_number in alerts and len(alerts[phone_number]) > alert_index:
                        alert = alerts[phone_number][-3:][alert_index]
                        response = "END Alert Details:\n"
                        response += f"Crop: {alert.get('crop', 'unknown')}\n"
                        response += f"Time: {alert.get('timestamp', 'unknown')}\n"
                        response += "Issues:\n"
                        for issue in alert.get('alerts', []):
                            response += f"- {issue}\n"
                    else:
                        response = "END Alert not found."
                else:
                    response = "END Invalid selection."
            
            elif state == "crop_advice":
                if text == "0":
                    users[phone_number]["state"] = "weather_alerts"
                    save_users(users)
                    response = "CON Weather Alerts:\n1. View Alerts\n2. Weather Forecast\n3. Crop Advice"
                elif text.isdigit():
                    if phone_number in harvests:
                        unique_crops = list(set(h['crop_type'] for h in harvests[phone_number]))
                        if 1 <= int(text) <= len(unique_crops):
                            selected_crop = unique_crops[int(text)-1].lower()
                            response = "END Crop Advice:\n"
                            
                            if phone_number in land_data and 'farm_address' in land_data[phone_number]:
                                weather = get_weather_data(land_data[phone_number]['farm_address'])
                                if weather:
                                    temp = weather.get('main', {}).get('temp', 0)
                                    if selected_crop in CROP_SENSITIVITY:
                                        thresholds = CROP_SENSITIVITY[selected_crop]
                                        if temp < thresholds['min_temp']:
                                            response += f"Protect {selected_crop} from cold with covers.\n"
                                        if temp > thresholds['max_temp']:
                                            response += f"Provide shade for {selected_crop} during hot hours.\n"
                            
                            response += f"Best practices for {selected_crop}:\n"
                            response += "- Ensure proper drainage\n"
                            response += "- Monitor for pests regularly\n"
                            response += "- Water in early morning\n"
                        else:
                            response = "END Invalid crop selection."
                    else:
                        response = "END No crops registered yet."
                else:
                    response = "END Invalid input."
        elif user_role == "investor":
            if state == "investor_menu":
                if text == "":
                    response = "CON Investor Dashboard:\n"
                    response += "1. Browse Farms\n"
                    response += "2. My Investments\n"
                    response += "3. Market Trends\n"
                    response += "4. Due Diligence Tools\n"
                    response += "5. Investor Profile"
                elif text == "1":
                    users[phone_number]["state"] = "browse_farms"
                    save_users(users)
                    response = "CON Browse Farms:\n1. By Location\n2. By Crop Type\n3. By ROI"
                elif text == "2":
                    investments = load_investments()
                    if phone_number in investments and investments[phone_number]:
                        users[phone_number]["state"] = "view_investments"
                        save_users(users)
                        response = "CON Your Investments:\n"
                        for i, inv in enumerate(investments[phone_number][-3:], 1):
                            response += f"{i}. {inv.get('farm_name', 'N/A')} - ${inv.get('amount', 0)}\n"
                        response += "Select to view details (1-3) or 0 to go back"
                    else:
                        response = "END You have no active investments."
                elif text == "3":
                    users[phone_number]["state"] = "market_trends"
                    save_users(users)
                    response = "CON Market Trends:\n1. Crop Prices\n2. Weather Impact\n3. Demand Forecast"
                elif text == "4":
                    users[phone_number]["state"] = "due_diligence"
                    save_users(users)
                    response = "CON Due Diligence:\n1. Farm Verification\n2. Historical Yields\n3. Risk Assessment"
                elif text == "5":
                    users[phone_number]["state"] = "investor_profile"
                    save_users(users)
                    response = "CON Investor Profile:\n1. View Profile\n2. Update Risk Profile\n3. Investment History"
                else:
                    response = "END Invalid selection."

            elif state == "browse_farms":
                if text == "":
                    response = "CON Browse Farms:\n1. By Location\n2. By Crop Type\n3. By ROI"
                elif text == "1":
                    users[phone_number]["state"] = "browse_by_location"
                    save_users(users)
                    response = "CON Enter region:\n1. Eastern\n2. Western\n3. Northern\n4. Southern"
                elif text == "2":
                    users[phone_number]["state"] = "browse_by_crop"
                    save_users(users)
                    response = "CON Select crop:\n1. Coffee\n2. Tea\n3. Maize\n4. Wheat"
                elif text == "3":
                    land_data = load_land_data()
                    available_farms = [f for f in land_data.values() if f.get('seeking_investment', False)]
                    sorted_farms = sorted(available_farms, key=lambda x: float(x.get('projected_roi', 0)), reverse=True)[:3]
                    
                    if sorted_farms:
                        users[phone_number]["state"] = "farm_details"
                        users[phone_number]["temp_farms"] = sorted_farms
                        save_users(users)
                        
                        response = "CON Top ROI Farms:\n"
                        for i, farm in enumerate(sorted_farms, 1):
                            response += f"{i}. {farm.get('farm_name')} - {farm.get('projected_roi')}% ROI\n"
                        response += "Select farm for details (1-3)"
                    else:
                        response = "END No farms currently seeking investment."
                else:
                    response = "END Invalid input."

            elif state == "farm_details":
                if text.isdigit() and 1 <= int(text) <= 3:
                    selected_farm = users[phone_number]["temp_farms"][int(text)-1]
                    users[phone_number]["temp_investment"] = {"farm_id": selected_farm.get('phone_number')}
                    users[phone_number]["state"] = "investment_amount"
                    save_users(users)
                    
                    response = "END Farm Details:\n"
                    response += f"Name: {selected_farm.get('farm_name')}\n"
                    response += f"Type: {selected_farm.get('farm_type')}\n"
                    response += f"Location: {selected_farm.get('farm_address')}\n"
                    response += f"ROI: {selected_farm.get('projected_roi')}%\n"
                    response += f"Seeking: ${selected_farm.get('fund_amount')}\n"
                    response += "CON Enter amount to invest:"
                else:
                    response = "END Invalid selection."

            elif state == "investment_amount":
                if text.isdigit():
                    amount = float(text)
                    farm_id = users[phone_number]["temp_investment"]["farm_id"]
                    farm_data = land_data.get(farm_id, {})
                    
                    if amount <= float(farm_data.get('fund_amount', 0)):
                        investments = load_investments()
                        if phone_number not in investments:
                            investments[phone_number] = []
                        
                        investments[phone_number].append({
                            "farm_id": farm_id,
                            "farm_name": farm_data.get('farm_name'),
                            "amount": amount,
                            "date": datetime.now().strftime("%Y-%m-%d"),
                            "status": "active",
                            "expected_roi": farm_data.get('projected_roi')
                        })
                        save_investments(investments)
                        
                        remaining = float(farm_data.get('fund_amount', 0)) - amount
                        land_data[farm_id]['fund_amount'] = str(remaining)
                        if remaining <= 0:
                            land_data[farm_id]['seeking_investment'] = False
                        save_land_data(land_data)
                        
                        response = "END Investment successful!\n"
                        response += f"${amount} invested in {farm_data.get('farm_name')}"
                    else:
                        response = "END Amount exceeds funding needs. Try lower amount."
                else:
                    response = "END Invalid amount. Numbers only."

            elif state == "market_trends":
                if text == "":
                    response = "CON Market Trends:\n1. Crop Prices\n2. Weather Impact\n3. Demand Forecast"
                elif text == "1":
                    response = "END Current Crop Prices:\n"
                    response += "Coffee: $2.50/kg\n"
                    response += "Tea: $1.80/kg\n"
                    response += "Maize: $0.30/kg\n"
                    response += "Wheat: $0.35/kg"
                elif text == "2":
                    response = "END Weather Impact:\n"
                    response += "Heavy rains expected\nin Western regions\nmay affect tea harvests"
                elif text == "3":
                    response = "END Demand Forecast:\n"
                    response += "Coffee: ↑12%\nTea: ↑5%\nMaize: ↓3%\nWheat: ↔"
                else:
                    response = "END Invalid selection."

            elif state == "due_diligence":
                if text == "":
                    response = "CON Due Diligence:\n1. Farm Verification\n2. Historical Yields\n3. Risk Assessment"
                elif text == "1":
                    if 'temp_investment' in users[phone_number]:
                        farm_id = users[phone_number]["temp_investment"]["farm_id"]
                        farm_data = land_data.get(farm_id, {})
                        
                        response = "END Farm Verification:\n"
                        response += f"Name: {farm_data.get('farm_name')}\n"
                        response += f"Certified: {bool(farm_data.get('certifications'))}\n"
                        response += f"Images: {bool(farm_data.get('farm_images'))}\n"
                        response += f"Collateral: {farm_data.get('collateral')}"
                    else:
                        response = "END Select a farm first."
                elif text == "2":
                    response = "END Historical Yields:\n"
                    response += "2022: 1200kg/ha\n"
                    response += "2021: 1100kg/ha\n"
                    response += "2020: 900kg/ha\n"
                    response += "(Sample data)"
                elif text == "3":
                    response = "END Risk Assessment:\n"
                    response += "Weather Risk: Medium\n"
                    response += "Market Risk: Low\n"
                    response += "Management Risk: Low"
                else:
                    response = "END Invalid selection."

            elif state == "investor_profile":
                if text == "":
                    response = "CON Investor Profile:\n1. View Profile\n2. Update Risk Profile\n3. Investment History"
                elif text == "1":
                    profile = users.get(phone_number, {})
                    response = "END Your Profile:\n"
                    response += f"Name: {profile.get('name', 'N/A')}\n"
                    response += f"Risk Appetite: {profile.get('risk_profile', 'Medium')}\n"
                    response += f"Total Invested: ${sum(inv.get('amount', 0) for inv in investments.get(phone_number, []))}"
                elif text == "2":
                    users[phone_number]["state"] = "update_risk_profile"
                    save_users(users)
                    response = "CON Your Risk Profile:\n1. Conservative\n2. Moderate\n3. Aggressive"
                elif text == "3":
                    investments = load_investments()
                    if phone_number in investments:
                        response = "END Investment History:\n"
                        for inv in investments[phone_number][-3:]:
                            response += f"{inv.get('date')}: ${inv.get('amount')} in {inv.get('farm_name')}\n"
                    else:
                        response = "END No investment history."
                else:
                    response = "END Invalid selection."

            elif state == "update_risk_profile":
                risk_levels = {"1": "Conservative", "2": "Moderate", "3": "Aggressive"}
                if text in risk_levels:
                    users[phone_number]["risk_profile"] = risk_levels[text]
                    users[phone_number]["state"] = "investor_profile"
                    save_users(users)
                    response = "END Risk profile updated to " + risk_levels[text]
                else:
                    response = "END Invalid selection."
    return response, 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run(port=5000)