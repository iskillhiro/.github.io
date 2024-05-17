from quotes import get_random_fishing_quote
import requests
from datetime import datetime, timedelta
from checkConditions import check_fishing_conditions
from bs4 import BeautifulSoup
from facts import get_random_fact

lat = 54.182241
lon = 49.658100
appid = 'ef5d7e8fb32b4b8caf8bc95b77771cad'
forecast_weather_url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={appid}&lang=ru&units=metric'

###
temp_url = "https://www.gismeteo.ru/weather-dimitrovgrad-4408/10-days/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
###


def get_forecast():
    try:
        # Запрос на API OpenWeather для получения прогноза
        response = requests.get(forecast_weather_url)
        response.raise_for_status()
        temp_response = requests.get(temp_url, headers=headers)
        if temp_response.status_code != 200:
            return f"Ошибка при доступе к Gismeteo: {temp_response.status_code}"
        temp_response.raise_for_status()
        soup = BeautifulSoup(temp_response.content, 'html.parser')
				
        # Извлечение данных о температуре
        temp_divs = soup.select('div.widget-row-chart-temperature .values .value')
        mid_div = soup.find(attrs={"data-row": "temperature-avg"})
        temperature_values = mid_div.find_all(class_="value")
        mid_temps = []
        for value in temperature_values:
            temp = value.find('span', class_='unit_temperature_c').text
            mid_temps.append(temp.replace('+', ''))

            
        temperatures = []
        for div in temp_divs[:4]:  # Получаем данные только на 4 дня
            max_temp = div.select_one('.maxt .unit_temperature_c').text
            min_temp = div.select_one('.mint .unit_temperature_c').text
            temperatures.append({
                'max_temp': max_temp.replace('°', ''),
                'min_temp': min_temp.replace('°', '')
            })
        
        # Получение данных прогноза из OpenWeather
        forecast_data = response.json()
        forecast_days = {}
        
        for entry in forecast_data['list']:
            date = datetime.fromtimestamp(entry['dt'])
            day = date.date()
            if day not in forecast_days:
                forecast_days[day] = entry

        forecasts = []
        today = datetime.now().date()
        for i in range(4):
            temp_data = temperatures[i]
            mid_temp = int(mid_temps[i])
            max_temp = temp_data['max_temp']
            min_temp = temp_data['min_temp']
            
            forecast_date = today + timedelta(days=i)
            if forecast_date in forecast_days:
                data = forecast_days[forecast_date]
                pressure_hpa = data.get('main', {}).get('pressure', 0)
                pressure_mm_hg = round(pressure_hpa * 0.75006, 2)
                
                forecast = (
                    f"📅 Дата: {forecast_date}\n"
                    f"🌥️ Состояние: {data['weather'][0]['description']} \n"
                    f"🌡️ Среднесуточная температура: {mid_temp}°C\n"
                    f"🌡️ Минимальная температура: {min_temp}°C \n"
                    f"🌡️ Максимальная температура: {max_temp}°C \n"
                    f"💧 Влажность: {data['main']['humidity']}% \n"
                    f"🌫️ Давление: {pressure_mm_hg} мм ртутного столба\n"
                    f"🌬️ Скорость ветра: {data['wind']['speed']} м/с \n"
                    f"🌬️ Направление ветра: {data['wind']['deg']}° \n"
                    f"🌬️ Порыв ветра: {data['wind'].get('gust', 'N/A')} м/с \n"
                    f"☁️ Облачность: {data['clouds']['all']}% \n"
                    f"🌧️ Видимость: {data.get('visibility', 'N/A')} м \n"
                    f"🌅 Рассвет: {data.get('sunrise', 'N/A')} м \n"
                    f"🌇 Закат: {data.get('sunset', 'N/A')} м \n"
                )
                
                if 'rain' in data:
                    forecast += f"🌧️ Дождь за последний час: {data['rain'].get('1h', 'N/A')} мм\n"
                    forecast += f"🌧️ Дождь за последние 3 часа: {data['rain'].get('3h', 'N/A')} мм\n"

                if 'snow' in data:
                    forecast += f"❄️ Снег за последний час: {data['snow'].get('1h', 'N/A')} мм\n"
                    forecast += f"❄️ Снег за последние 3 часа: {data['snow'].get('3h', 'N/A')} мм\n"
                
                forecast += f"\n{check_fishing_conditions(data, mid_temp, int(max_temp))}"
                forecasts.append(forecast)
        
        return '\n\n\n'.join(forecasts) + f"\n\n💡Интересный факт\n{get_random_fact()}" + f"\n\n🦈 {get_random_fishing_quote()[:-1]} 🦈"
            
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"
