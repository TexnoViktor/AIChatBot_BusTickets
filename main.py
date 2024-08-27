import sqlite3
import spacy
import uuid

# Завантаження української моделі spaCy
nlp = spacy.load("uk_core_news_md")


# Створення підключення до бази даних
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(e)
    return conn


# Отримання всіх записів із таблиць
def fetch_table_data(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT departure_city, destination_city FROM Routes")
    routes = cursor.fetchall()

    cursor.execute("SELECT bus_number FROM Buses")
    buses = cursor.fetchall()

    cursor.execute("SELECT first_name, last_name FROM Clients")
    clients = cursor.fetchall()

    cursor.execute("SELECT bus_number, departure_time, total_seats, available_seats FROM Buses")
    bus_info = cursor.fetchall()

    cursor.execute("SELECT client_id, first_name, last_name FROM Clients")
    client_info = cursor.fetchall()

    return {
        "routes": routes,
        "buses": buses,
        "clients": clients,
        "bus_info": bus_info,
        "client_info": client_info
    }


# Обробка даних із бази за допомогою spaCy
def process_data_with_spacy(data):
    processed_data = {"routes": [], "buses": [], "clients": [], "bus_info": [], "client_info": []}

    # Обробка маршрутів
    for route in data["routes"]:
        dep_city, dest_city = route
        dep_doc = nlp(dep_city)
        dest_doc = nlp(dest_city)
        processed_data["routes"].append({
            "departure_city": dep_doc,
            "destination_city": dest_doc
        })

    # Обробка автобусів
    for bus in data["buses"]:
        bus_doc = nlp(bus[0])
        processed_data["buses"].append(bus_doc)

    # Обробка клієнтів
    for client in data["clients"]:
        first_name_doc = nlp(client[0])
        last_name_doc = nlp(client[1])
        processed_data["clients"].append({
            "first_name": first_name_doc,
            "last_name": last_name_doc
        })

    # Обробка додаткової інформації про автобуси
    for bus_info in data["bus_info"]:
        bus_number_doc = nlp(bus_info[0])
        departure_time_doc = nlp(bus_info[1])
        processed_data["bus_info"].append({
            "bus_number": bus_number_doc,
            "departure_time": departure_time_doc,
            "total_seats": bus_info[2],
            "available_seats": bus_info[3]
        })

    # Обробка додаткової інформації про клієнтів
    for client_info in data["client_info"]:
        first_name_doc = nlp(client_info[1])
        last_name_doc = nlp(client_info[2])
        processed_data["client_info"].append({
            "client_id": client_info[0],
            "first_name": first_name_doc,
            "last_name": last_name_doc
        })

    return processed_data


# Пошук найбільш відповідного елемента
def find_best_match(input_doc, candidates):
    best_match = None
    best_score = 0.0

    for candidate in candidates:
        score = input_doc.similarity(candidate)
        if score > best_score:
            best_match = candidate
            best_score = score

    return best_match, best_score


# Функція для обробки вводу користувача
def process_user_input(input_text, processed_data):
    input_doc = nlp(input_text.lower())
    results = {}

    # Пошук маршруту
    best_route_match = None
    best_route_score = 0.0
    for route in processed_data["routes"]:
        dep_city_match, dep_city_score = find_best_match(input_doc, [route["departure_city"]])
        dest_city_match, dest_city_score = find_best_match(input_doc, [route["destination_city"]])

        total_score = dep_city_score + dest_city_score
        if total_score > best_route_score:
            best_route_match = route
            best_route_score = total_score

    results["route"] = best_route_match

    # Пошук автобусу
    best_bus_match, best_bus_score = find_best_match(input_doc, processed_data["buses"])
    results["bus"] = best_bus_match

    # Пошук клієнта
    best_client_match = None
    best_client_score = 0.0
    for client in processed_data["clients"]:
        first_name_match, first_name_score = find_best_match(input_doc, [client["first_name"]])
        last_name_match, last_name_score = find_best_match(input_doc, [client["last_name"]])

        total_score = first_name_score + last_name_score
        if total_score > best_client_score:
            best_client_match = client
            best_client_score = total_score

    results["client"] = best_client_match

    return results


# Додаткові функції для роботи з квитками
def create_ticket(conn, client_id, bus_id, seat_number, trip_date_id, departure_time, price):
    cursor = conn.cursor()
    ticket_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO Tickets (ticket_id, client_id, bus_id, seat_number, trip_date_id, departure_time, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (ticket_id, client_id, bus_id, seat_number, trip_date_id, departure_time, price))
    cursor.execute("UPDATE Buses SET available_seats = available_seats - 1 WHERE bus_id = ?", (bus_id,))
    conn.commit()
    return ticket_id


def cancel_ticket(conn, ticket_id):
    cursor = conn.cursor()
    cursor.execute("SELECT bus_id FROM Tickets WHERE ticket_id = ?", (ticket_id,))
    bus_id = cursor.fetchone()
    if bus_id:
        cursor.execute("DELETE FROM Tickets WHERE ticket_id = ?", (ticket_id,))
        cursor.execute("UPDATE Buses SET available_seats = available_seats + 1 WHERE bus_id = ?", (bus_id[0],))
        conn.commit()
        return True
    return False


# Функції для взаємодії з адміністратором
def add_client(conn, first_name, last_name, birth_date, email, phone):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Clients (first_name, last_name, birth_date, email, phone) VALUES (?, ?, ?, ?, ?)",
                   (first_name, last_name, birth_date, email, phone))
    conn.commit()
    print(f"Клієнт {first_name} {last_name} доданий!")


def add_route(conn, departure_city, destination_city, price):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Routes (departure_city, destination_city, price) VALUES (?, ?, ?)",
                   (departure_city, destination_city, price))
    conn.commit()
    print(f"Маршрут з {departure_city} до {destination_city} доданий!")


def delete_route(conn, route_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Routes WHERE route_id = ?", (route_id,))
    conn.commit()
    print(f"Маршрут {route_id} видалений!")


def list_clients(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT client_id, first_name, last_name FROM Clients")
    clients = cursor.fetchall()
    print("\nКлієнти:")
    for client in clients:
        print(f"ID: {client[0]}, Ім'я: {client[1]}, Прізвище: {client[2]}")


def list_routes(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT route_id, departure_city, destination_city, price FROM Routes")
    routes = cursor.fetchall()
    print("\nМаршрути:")
    for route in routes:
        print(f"ID: {route[0]}, Звідки: {route[1]}, Куди: {route[2]}, Ціна: {route[3]}")


# Пошук та виведення інформації про маршрути
def route_info(conn, departure_city=None, destination_city=None):
    cursor = conn.cursor()
    query = "SELECT route_id, departure_city, destination_city, price FROM Routes WHERE 1=1"
    params = []

    if departure_city:
        query += " AND departure_city = ?"
        params.append(departure_city)
    if destination_city:
        query += " AND destination_city = ?"
        params.append(destination_city)

    cursor.execute(query, params)
    routes = cursor.fetchall()

    if not routes:
        print("Немає доступних маршрутів.")
        return

    print("\nДоступні маршрути:")
    for route in routes:
        print(f"Звідки: {route[1]}, Куди: {route[2]}, Ціна: {route[3]}")


# Пошук та виведення інформації про автобуси
def bus_info(conn, bus_number=None):
    cursor = conn.cursor()
    query = "SELECT bus_number, departure_time, total_seats, available_seats FROM Buses WHERE 1=1"
    params = []

    if bus_number:
        query += " AND bus_number = ?"
        params.append(bus_number)

    cursor.execute(query, params)
    buses = cursor.fetchall()

    if not buses:
        print("Немає інформації про автобуси.")
        return

    print("\nДоступні автобуси:")
    for bus in buses:
        print(f"Номер автобуса: {bus[0]}, Відправлення: {bus[1]}, Всього місць: {bus[2]}, Доступних місць: {bus[3]}")


# Ознайомча інформація за містами
def city_info(conn, city_name):
    cursor = conn.cursor()
    cursor.execute(
        "SELECT departure_city, destination_city, price FROM Routes WHERE departure_city = ? OR destination_city = ?",
        (city_name, city_name))
    routes = cursor.fetchall()

    if not routes:
        print(f"Немає доступних маршрутів для міста {city_name}.")
        return

    print(f"\nМаршрути, що відправляються з або прибувають до міста {city_name}:")
    for route in routes:
        print(f"Звідки: {route[0]}, Куди: {route[1]}, Ціна: {route[2]}")


def admin_commands(conn, processed_data):
    while True:
        command = input("Адмін> ").strip().lower()
        doc = nlp(command)
        tokens = [token.lemma_ for token in doc]

        print(f"Розпізнані леми команди: {tokens}")

        if "додати" in tokens and "клієнт" in tokens:
            first_name = input("Введіть ім'я клієнта: ")
            last_name = input("Введіть прізвище клієнта: ")
            birth_date = input("Введіть дату народження (рррр-мм-дд): ")
            email = input("Введіть електронну пошту: ")
            phone = input("Введіть номер телефону: ")
            add_client(conn, first_name, last_name, birth_date, email, phone)

        elif "додати" in tokens and "маршрут" in tokens:
            departure_city = input("Звідки вирушає маршрут: ")
            destination_city = input("Куди прямує маршрут: ")
            price = float(input("Введіть ціну квитка: "))
            add_route(conn, departure_city, destination_city, price)

        elif "видалити" in tokens and "маршрут" in tokens:
            list_routes(conn)
            route_id = int(input("Введіть ID маршруту для видалення: "))
            delete_route(conn, route_id)

        elif "переглянути" in tokens and "клієнт" in tokens:
            list_clients(conn)

        elif "переглянути" in tokens and "маршрут" in tokens:
            list_routes(conn)

        elif "інформація" in tokens and "автобус" in tokens:
            bus_number = input("Введіть номер автобуса (або залиште порожнім для всіх): ").strip()
            bus_info(conn, bus_number if bus_number else None)

        elif "інформація" in tokens and "місто" in tokens:
            city_name = input("Введіть назву міста: ").strip()
            city_info(conn, city_name)

        elif "інформація" in tokens and "маршрут" in tokens:
            departure_city = input("Введіть назву міста відправлення (або залиште порожнім): ").strip()
            destination_city = input("Введіть назву міста призначення (або залиште порожнім): ").strip()
            route_info(conn, departure_city if departure_city else None, destination_city if destination_city else None)

        elif "вихід" in tokens or "до побачення" in tokens or "прощай" in tokens or "бувай" in tokens:
            print("Вихід з профілю адміністратора.")
            break

        else:
            print("Команда не розпізнана. Спробуйте ще раз.")


# Взаємодія з користувачем
def user_commands(conn, processed_data):
    while True:
        command = input("Користувач> ").strip().lower()
        doc = nlp(command)
        tokens = [token.lemma_ for token in doc]

        print(f"Розпізнані леми команди: {tokens}")

        if "купити" in tokens or "замовити" in tokens and "квиток" in tokens:
            departure_city = input("Звідки виїжджаєте: ")
            destination_city = input("Куди прямуєте: ")
            date = input("Введіть дату поїздки (рррр-мм-дд): ")

            cursor = conn.cursor()
            cursor.execute("""
                SELECT B.bus_id, B.bus_number, B.departure_time, B.available_seats, T.trip_date_id, R.price
                FROM Buses B
                JOIN Routes R ON B.route_id = R.route_id
                JOIN TripDates T ON R.route_id = T.route_id
                WHERE R.departure_city = ? AND R.destination_city = ? AND T.trip_date = ? AND B.available_seats > 0
                ORDER BY B.departure_time
            """, (departure_city, destination_city, date))
            buses = cursor.fetchall()

            if not buses:
                print("Немає доступних автобусів на цей маршрут і дату.")
                continue

            bus = buses[0]
            bus_id, bus_number, departure_time, available_seats, trip_date_id, price = bus
            seat_number = available_seats

            client_name = input("Введіть ваше ім'я: ")
            client_surname = input("Введіть ваше прізвище: ")

            cursor.execute("SELECT client_id FROM Clients WHERE first_name = ? AND last_name = ?",
                           (client_name, client_surname))
            client = cursor.fetchone()

            if not client:
                print("Клієнт не знайдений. Будь ласка, додайте свої дані.")
                first_name = client_name
                last_name = client_surname
                birth_date = input("Введіть дату народження (рррр-мм-дд): ")
                email = input("Введіть електронну пошту: ")
                phone = input("Введіть номер телефону: ")
                add_client(conn, first_name, last_name, birth_date, email, phone)

                cursor.execute("SELECT client_id FROM Clients WHERE first_name = ? AND last_name = ?",
                               (first_name, last_name))
                client = cursor.fetchone()

            ticket_id = create_ticket(conn, client[0], bus_id, seat_number, trip_date_id, departure_time, price)
            print(f"Квиток замовлений! Ваш номер квитка: {ticket_id}")
            print(f"Автобус: {bus_number}, Відправлення о {departure_time}, Ціна квитка: {price}")

        elif "скасувати" in tokens or "відмінити" in tokens and "квиток" in tokens:
            ticket_id = input("Введіть номер квитка: ")
            if cancel_ticket(conn, ticket_id):
                print("Квиток успішно скасовано.")
            else:
                print("Квиток не знайдений.")

        elif "інформація" in tokens and "автобус" in tokens:
            bus_number = input("Введіть номер автобуса (або залиште порожнім для всіх): ").strip()
            bus_info(conn, bus_number if bus_number else None)

        elif "інформація" in tokens and "місто" in tokens:
            city_name = input("Введіть назву міста: ").strip()
            city_info(conn, city_name)

        elif "інформація" in tokens and "маршрут" in tokens:
            departure_city = input("Введіть назву міста відправлення (або залиште порожнім): ").strip()
            destination_city = input("Введіть назву міста призначення (або залиште порожнім): ").strip()
            route_info(conn, departure_city if departure_city else None, destination_city if destination_city else None)

        elif "вихід" in tokens or "до побачення" in tokens or "прощай" in tokens or "бувай" in tokens:
            print("Вихід з профілю користувача.")
            break

        else:
            print("Команда не розпізнана. Спробуйте ще раз.")


# Основна функція
def main():
    database = "BusTicketsDB.sqlite"
    conn = create_connection(database)
    if conn:
        data = fetch_table_data(conn)
        processed_data = process_data_with_spacy(data)

        profile = input("Введіть ваш профіль (адмін/користувач): ").strip().lower()

        if profile == "адмін":
            print("Ви ввійшли як адміністратор.")
            admin_commands(conn, processed_data)
        elif profile == "користувач":
            print("Ви ввійшли як користувач.")
            user_commands(conn, processed_data)
        else:
            print("Невідомий профіль. Завершення програми.")

        conn.close()


if __name__ == "__main__":
    main()
