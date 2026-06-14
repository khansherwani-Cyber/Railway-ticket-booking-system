from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# ==========================================
# OOP CODE STRUCTURE
# ==========================================

class Train:
    def __init__(self, train_no, route, time, platform, seats, price):
        self.train_no = train_no
        self.route = route
        self.time = time
        self.platform = platform
        self.total_seats = seats
        self.price = price

    def to_dict(self, current_bookings):
        # Calculate remaining seats dynamically
        booked_count = sum(1 for b in current_bookings if b.train_no == self.train_no)
        return {
            "train_no": self.train_no,
            "route": self.route,
            "time": self.time,
            "platform": self.platform,
            "seats": self.total_seats - booked_count,
            "price": self.price
        }

class Booking:
    def __init__(self, ticket_no, train_no, name, father, cnic, time, platform, status, price):
        self.ticket_no = ticket_no
        self.train_no = train_no
        self.name = name
        self.father = father
        self.cnic = cnic
        self.time = time
        self.platform = platform
        self.status = status
        self.price = price

    def to_dict(self):
        return self.__dict__

class RailwaySystem:
    def __init__(self):
        self.trains = []
        self.bookings = []
        self.ticket_counter = 1000
        self.admin_password = "admin123"
        self._initialize_default_trains()

    def _initialize_default_trains(self):
        default_data = [
            ("101", "Karachi to Lahore", "08:00 AM", "1", 50, 1200),
            ("102", "Lahore to Islamabad", "09:30 AM", "2", 50, 900),
            ("103", "Peshawar to Quetta", "10:00 AM", "3", 50, 1500),
            ("104", "Multan to Faisalabad", "11:15 AM", "4", 50, 800),
            ("105", "Hyderabad to Sukkur", "01:00 PM", "5", 50, 700),
            ("106", "Rawalpindi to Bahawalpur", "02:30 PM", "6", 50, 1100),
            ("107", "Gujranwala to Sialkot", "04:00 PM", "7", 50, 650),
            ("108", "Layyah to Rahim Yar Khan", "06:45 PM", "8", 50, 2000),
            ("109", "Islamabad to Rahim Yar Khan", "08:45 PM", "5", 50, 2500),
            ("110", "Rahim Yar Khan to Hyderabad", "04:45 PM", "2", 50, 4000),
        ]
        for t in default_data:
            self.trains.append(Train(*t))

    def get_all_trains(self):
        return [t.to_dict(self.bookings) for t in self.trains]

    def count_user_tickets(self, cnic):
        return sum(1 for b in self.bookings if b.cnic == cnic)

    def book_tickets(self, train_no, passenger_list):
        train = next((t for t in self.trains if t.train_no == train_no), None)
        if not train:
            return {"success": False, "message": "Train not found."}

        # Calculate dynamic available seats
        booked_count = sum(1 for b in self.bookings if b.train_no == train_no)
        available_seats = train.total_seats - booked_count

        if len(passenger_list) > available_seats:
            return {"success": False, "message": f"Not enough seats available. Only {available_seats} left."}
        if len(passenger_list) > 5:
            return {"success": False, "message": "You can book a maximum of 5 tickets at once."}

        # First validation pass for CNIC limits
        for p in passenger_list:
            cnic = p.get('cnic', '').strip()
            if len(cnic) != 13 or not cnic.isdigit():
                return {"success": False, "message": f"Invalid CNIC format: {cnic}"}
            if self.count_user_tickets(cnic) >= 2:
                return {"success": False, "message": f"CNIC {cnic} already has 2 active tickets."}

        # Process bookings
        new_receipts = []
        for p in passenger_list:
            self.ticket_counter += 1
            status = random.choice(["On Time", "Delayed"])
            new_booking = Booking(
                ticket_no=self.ticket_counter,
                train_no=train_no,
                name=p['name'].strip(),
                father=p['father'].strip(),
                cnic=p['cnic'].strip(),
                time=train.time,
                platform=train.platform,
                status=status,
                price=train.price
            )
            self.bookings.append(new_booking)
            new_receipts.append(new_booking.to_dict())

        return {"success": True, "tickets": new_receipts}

    def cancel_ticket(self, ticket_no):
        for b in self.bookings:
            if b.ticket_no == ticket_no:
                self.bookings.remove(b)
                return {"success": True, "message": f"Ticket #{ticket_no} cancelled successfully."}
        return {"success": False, "message": "Ticket number not found."}


# Initialize the core OOP backend system
system = RailwaySystem()

# ==========================================
# FLASK ROUTING (Web Endpoints)
# ==========================================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/trains', methods=['GET'])
def api_get_trains():
    return jsonify(system.get_all_trains())

@app.route('/api/book', methods=['POST'])
def api_book():
    data = request.json
    train_no = data.get('train_no')
    passengers = data.get('passengers', [])
    result = system.book_tickets(train_no, passengers)
    return jsonify(result)

@app.route('/api/cancel', methods=['POST'])
def api_cancel():
    data = request.json
    try:
        t_no = int(data.get('ticket_no'))
        result = system.cancel_ticket(t_no)
        return jsonify(result)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid Ticket Number format."})

if __name__ == '__main__':
    app.run(debug=True)
