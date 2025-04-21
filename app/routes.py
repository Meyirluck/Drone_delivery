from flask import Blueprint, render_template, request, jsonify, redirect, url_for

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/observe')
def observe():
    return render_template('observe.html')

@main.route('/submit_order', methods=['POST'])
def submit_order():
    # Тут можно сохранить заказ, например в базу или лог
    first_name = request.form.get('firstName')
    last_name = request.form.get('lastName')
    phone_number = request.form.get('phoneNumber')
    restaurant = request.form.get('restaurant')
    print(f"Order from {first_name} {last_name} ({phone_number}) for {restaurant}")

    return jsonify({'redirect_url': url_for('main.observe')})

@main.route('/get_positions')
def get_positions():
    # Это пример. Ты можешь получать данные из модели, БД или модуля.
    drone_data = [{
        "id": "DRONE_001",
        "battery": 85,
        "weather": "Ясно",
        "temp": 22,
        "humidity": 40,
        "wind_speed": 3,
        "gps": [43.1965135, 76.6309754]
    }]
    return jsonify(drone_data)

@main.route('/calculate_eta', methods=['POST'])
def calculate_eta():
    try:
        lat = float(request.form.get('lat'))
        lon = float(request.form.get('lon'))
        # Сюда добавь реальную логику расчета
        eta = 5.3  # в минутах
        return jsonify({"eta": eta})
    except Exception as e:
        return jsonify({"error": "Ошибка при расчете ETA"}), 400

@main.route('/start_drone', methods=['POST'])
def start_drone():
    lat = float(request.form.get('lat'))
    lon = float(request.form.get('lon'))
    # Тут можешь проверить батарею, стартовать дрон и т.п.
    battery_level = 85
    if battery_level < 20:
        return jsonify({"error": "Батарея слишком низкая"}), 400
    return jsonify({"status": "ok"})
