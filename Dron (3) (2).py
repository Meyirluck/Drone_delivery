from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import threading
import requests
from geopy.distance import geodesic
import time

app = Flask(__name__)

# Инициализация дрона
basic_location = [43.1965135, 76.6309754] # Начальное местоположение (база)
home_location = [43.1965135, 76.6309754]
drones = [
    {"id": 1, "gps": home_location[:], "battery": 100, "weather": "Clear", "temp": 20, "humidity": 20, "wind_speed": 5}
]

MAX_DISTANCE_KM = 15  # Максимальная дистанция полета дрона
WEATHER_API_KEY = "e1428d305aeb0b8fd12cc307c9df2937"

# Дрон в пути или нет
drone_in_transit = False
target_location = None


# Получение текущей погоды
def get_weather(lat, lon):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url)
        weather_data = response.json()
        return {
            "description": weather_data["weather"][0]["description"],
            "temp": weather_data["main"]["temp"],
            "humidity": weather_data["main"]["humidity"],
            "wind_speed": weather_data["wind"]["speed"]
        }
    except Exception:
        return {"description": "Unknown", "temp": 0, "humidity": 0, "wind_speed": 0}


# Проверка погодных условий
def check_weather_conditions(humidity, wind_speed):
    return humidity <= 75 and wind_speed <= 10

# Добавляем координаты для каждого ресторана
RESTAURANT_LOCATIONS = {
    "Salam Bro": [43.202916, 76.621598],  # координаты для Salam Bro
    "KFC": [43.199715, 76.634548],  # координаты для KFC
    "YOLO": [43.206845, 76.664520]  # координаты для YOLO
}

# Движение дрона к выбранному местоположению
def move_drone():
    global drone_in_transit, target_location, home_location
    while True:
        if drone_in_transit and target_location:
            drone = drones[0]
            current_location = drones[0]["gps"]
            distance = geodesic(current_location, target_location).km

            # Если дрон достиг точки назначения
            if distance < 0.01:
                if target_location != basic_location:
                    print("Дрон достиг пункта назначения!")
                    # Ожидание 10 секунд на месте
                    time.sleep(10)
                    # Возвращаемся на базу
                    target_location = basic_location
                    print("Дрон возвращается на ресторан!")
                else:
                    drone_in_transit = False
                    target_location = None
                    print("Дрон вернулся на ресторан!")
                continue

            # Двигаем дрон к точке назначения
            step_distance = (100 / 3600) * 5  # Скорость: 100 км/ч, шаг: 5 секунд
            distance = geodesic(current_location, target_location).km

            if step_distance >= distance:
                # Если шаг больше или равен оставшемуся расстоянию, дрон достигает точки назначения
                drones[0]["gps"] = target_location
            else:
                # Иначе продолжаем движение в сторону цели
                fraction = step_distance / distance
                new_lat = current_location[0] + (target_location[0] - current_location[0]) * fraction
                new_lon = current_location[1] + (target_location[1] - current_location[1]) * fraction
                drones[0]["gps"] = [new_lat, new_lon]

            home_location = drones[0]["gps"]

            # Уменьшаем заряд батареи
            drone["battery"] = max(drone["battery"] - 1, 0)

        time.sleep(5)


# Мониторинг состояния дрона (погода и заряд батареи)
def monitor_drones():
    global drone_in_transit
    while True:
        for drone in drones:
            # Обновление погоды
            weather = get_weather(*drone["gps"])
            drone["weather"] = weather["description"]
            drone["temp"] = weather["temp"]
            drone["humidity"] = weather["humidity"]
            drone["wind_speed"] = weather["wind_speed"]

# Уменьшаем заряд батареи
            if drone["battery"] > 0:
                drone["battery"] -= 1

            # Если заряд батареи меньше 20%, дрон не может принимать заказы
            if drone["battery"] < 20 and drone_in_transit:
                print("Низкий заряд батареи, дрон не принимает заказы.")
                drone_in_transit = False

        time.sleep(60)  # Уменьшаем заряд батареи раз в минуту


# Уведомление о прибытии дрона на карту
@app.route('/drone_arrived', methods=['POST'])
def drone_arrived():
    data = request.json
    if data.get("status") == "arrived":
        print("Дрон прибыл! Уведомление отправлено на карту.")
    return jsonify({"message": "Уведомление получено."})


@app.route('/')
def index():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <title>Order Delivery</title>
        </head>
        <body>
            <div class="container mt-5">
                <h1 class="text-center">Place Your Order</h1>
                <form id="order-form" class="mt-4">
                    <div class="mb-3">
                        <label for="first-name" class="form-label">First Name</label>
                        <input type="text" id="first-name" name="firstName" class="form-control" placeholder="Enter your first name" required>
                    </div>
                    <div class="mb-3">
                        <label for="last-name" class="form-label">Last Name</label>
                        <input type="text" id="last-name" name="lastName" class="form-control" placeholder="Enter your last name" required>
                    </div>
                    <div class="mb-3">
                        <label for="phone-number" class="form-label">Phone Number</label>
                        <input type="tel" id="phone-number" name="phoneNumber" class="form-control" placeholder="Enter your phone number" pattern="[0-9]+" title="Phone number should only contain numbers" required>
                    </div>
                    <div class="mb-3">
                        <label for="restaurant" class="form-label">Select Restaurant</label>
                        <select id="restaurant" name="restaurant" class="form-select" required>
                            <option value="" disabled selected>Select a restaurant</option>
                            <option value="Salam Bro">Salam Bro</option>
                            <option value="KFC">KFC</option>
                            <option value="YOLO">YOLO</option>
                        </select>
                    </div>
                    <button type="submit" class="btn btn-primary">Submit Order</button>
                </form>
                <div id="response-message" class="mt-4"></div>
            </div>

            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script>
                $(document).ready(function() {
                    $('#order-form').on('submit', function(e) {
                        e.preventDefault();

                        const orderData = $(this).serialize();  

                        $.post('/submit_order', orderData, function(response) {
                            if (response.redirect_url) {
                                window.location.href = response.redirect_url; // Перенаправление на страницу наблюдения
                            }
                        }).fail(function() {
                            $('#response-message').html(`
                                <div class="alert alert-danger">
                                    Something went wrong. Please try again.
                                </div>
                            `);
                        });
                    });

                });
            </script>
        </body>
        </html>
    """)

@app.route('/submit_order', methods=['POST'])
def submit_order():
    global basic_location

    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    phone_number = request.form.get('phoneNumber')
    restaurant = request.form.get('restaurant')

    # Обработка данных (например, сохранение в базу данных)
    print(f"Order received from {first_name} {last_name} ({phone_number}) for {restaurant}")

    if restaurant not in RESTAURANT_LOCATIONS:
        return jsonify({'error': "Неизвестный ресторан."})

    # Устанавливаем точку назначения на основании выбранного ресторана
    drones[0]["gps"] = RESTAURANT_LOCATIONS[restaurant]
    basic_location = RESTAURANT_LOCATIONS[restaurant]

    # Перенаправление на страницу наблюдения
    return jsonify({"redirect_url": url_for('observe')})


# Главная страница с картой
@app.route('/observe')
def observe():
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link rel="stylesheet" href="https://unpkg.com/leaflet/dist/leaflet.css" />
            <script src="https://unpkg.com/leaflet/dist/leaflet.js"></script>
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
        </head>
        <body style="margin: 0;">
            <div id="map" style="width: 100%; height: 100vh;"></div>
            <script>
    var map = L.map('map').setView([43.1965135, 76.6309754], 14);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

    var userMarker;
    var droneMarker;
    var routeLine;

    // Кастомная иконка для дрона
    var droneIcon = L.icon({
        iconUrl: 'https://pngimg.com/uploads/drone/drone_PNG133.png',
        iconSize: [50, 50]
    });

    // Отображение дрона
    function updateDrone() {
        $.get('/get_positions', function(data) {
            if (data.length > 0) {
                var drone = data[0];
                var latLng = [drone.gps[0], drone.gps[1]];

                if (droneMarker) {
                    droneMarker.setLatLng(latLng).getPopup().setContent(`
                        <b>Дрон ID:</b> ${drone.id}<br>
                        <b>Батарея:</b> ${drone.battery}%<br>
                        <b>Погода:</b> ${drone.weather}<br>
                        <b>Температура:</b> ${drone.temp}°C<br>
                        <b>Влажность:</b> ${drone.humidity}%<br>
                        <b>Скорость ветра:</b> ${drone.wind_speed} м/с
                    `);
                } else {
                    droneMarker = L.marker(latLng, { icon: droneIcon })
                        .addTo(map)
                        .bindPopup(`
                            <b>Дрон ID:</b> ${drone.id}<br>
                            <b>Батарея:</b> ${drone.battery}%<br>
                            <b>Погода:</b> ${drone.weather}<br>
                            <b>Температура:</b> ${drone.temp}°C<br>
                            <b>Влажность:</b> ${drone.humidity}%<br>
                            <b>Скорость ветра:</b> ${drone.wind_speed} м/с
                        `)
                        .openPopup();
                }

                // Если маршрут уже создан, обновляем его
                if (userMarker && routeLine) {
                    routeLine.setLatLngs([latLng, userMarker.getLatLng()]);
                }
            }
        });
    }


    // Обработка клика по карте
    map.on('click', function(e) {
        const latitude = e.latlng.lat;
        const longitude = e.latlng.lng;

        // Обновляем маркер пользователя
        if (userMarker) {
            userMarker.setLatLng([latitude, longitude]);
        } else {
            userMarker = L.marker([latitude, longitude]).addTo(map)
                .bindPopup("Ваше местоположение")
                .openPopup();
        }

// Обновляем линию маршрута
        if (droneMarker) {
            const droneLatLng = droneMarker.getLatLng();
            const userLatLng = [latitude, longitude];

            if (routeLine) {
                routeLine.setLatLngs([droneLatLng, userLatLng]);
            } else {
                routeLine = L.polyline([droneLatLng, userLatLng], { color: 'blue' }).addTo(map);
            }
        }

        // Запрос на расчёт ETA
        $.post('/calculate_eta', { lat: latitude, lon: longitude }, function(response) {
            if (response.error) {
                alert(response.error);
            } else {
                if (confirm(`Время прибытия дрона: ${response.eta.toFixed(2)} минут. Запустить дрон?`)) {
                    $.post('/start_drone', { lat: latitude, lon: longitude })
                        .done(function(response) {
                            if (response.error) {
                                // Показываем сообщение, что дрон не может принять заказ
                                alert(response.error);
                                var alertMessage = L.popup()
                                    .setLatLng([latitude, longitude])
                                    .setContent("Дрон временно не может принять заказ: низкий заряд батареи.")
                                    .openOn(map);
                            } else {
                                alert('Дрон запущен.');
                            }
                        });
                }
            }
        });
    });

    // Обновляем данные каждые 10 секунд
    setInterval(updateDrone, 10000);
    updateDrone();
</script>

        </body>
        </html>
    """)


# Получение текущих позиций дронов
@app.route('/get_positions')
def get_positions():
    print(f"Текущая позиция дрона: {drones[0]['gps']}, цель: {target_location}")
    return jsonify(drones)


# Расчёт времени прибытия с учетом погодных условий
@app.route('/calculate_eta', methods=['POST'])
def calculate_eta_route():
    user_lat = float(request.form['lat'])
    user_lon = float(request.form['lon'])
    user_location = (user_lat, user_lon)
    drone = drones[0]
    drone_location = tuple(drone["gps"])

    if not check_weather_conditions(drone["humidity"], drone["wind_speed"]):
        return jsonify(
            {'error': "Дрон не может лететь: плохие погодные условия (высокая влажность или сильный ветер)."})

    distance = geodesic(drone_location, user_location).km
    if distance > MAX_DISTANCE_KM:
        return jsonify({'error': f"Дрон не может лететь так далеко! Максимальная дистанция: {MAX_DISTANCE_KM} км."})

    eta = distance / 100 * 60
    return jsonify({'eta': eta})


# Функция для старта дрона с учетом выбранного ресторана
@app.route('/start_drone', methods=['POST'])
def start_drone():
    global drone_in_transit, target_location
    # Проверка, если заряд батареи меньше 20%
    if drones[0]["battery"] < 20:
        return jsonify({'error': "Дрон не может принять заказ: низкий заряд батареи."})

    # Запуск дрона
    target_location = [float(request.form['lat']), float(request.form['lon'])]
    drone_in_transit = True
    return jsonify({'status': 'Дрон запущен'})


if __name__ == "__main__":
    threading.Thread(target=monitor_drones, daemon=True).start()
    threading.Thread(target=move_drone, daemon=True).start()
    app.run(debug=True, use_reloader=False)