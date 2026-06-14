# =============================================================================
# Smart Phone Book - Backend
# University OOP Project | Python + Flask
# File: app.py
# =============================================================================
# OOP Structure:
#   - Contact     : Represents a single contact entity
#   - PhoneBook   : Manages the collection of contacts
#   - Flask routes: Bridge between frontend and OOP backend via JSON API
# =============================================================================

import re
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)


# =============================================================================
# CLASS 1: Contact
# Represents a single contact. Encapsulates all attributes of one person.
# =============================================================================
class Contact:
    def __init__(self, name: str, phone: str, email: str, category: str):
        """
        Constructor: creates a new Contact object.
        All inputs are stripped of whitespace to avoid dirty data.
        """
        self.__name     = name.strip()
        self.__phone    = phone.strip()
        self.__email    = email.strip()
        self.__category = category.strip()

    # ---------- Getters (read-only access to private attributes) ----------
    def get_name(self)     -> str: return self.__name
    def get_phone(self)    -> str: return self.__phone
    def get_email(self)    -> str: return self.__email
    def get_category(self) -> str: return self.__category

    def to_dict(self) -> dict:
        """Serializes the Contact object to a plain dictionary for JSON responses."""
        return {
            "name":     self.__name,
            "phone":    self.__phone,
            "email":    self.__email,
            "category": self.__category
        }

    def __repr__(self) -> str:
        return f"Contact(name='{self.__name}', phone='{self.__phone}', category='{self.__category}')"


# =============================================================================
# CLASS 2: PhoneBook
# Manages a list of Contact objects. All business logic lives here.
# =============================================================================
class PhoneBook:
    VALID_CATEGORIES = {"Family", "Work", "Friends", "General"}

    def __init__(self):
        """
        Constructor: initializes the private contact list and loads sample data.
        """
        self.__contacts: list[Contact] = []
        self.__load_sample_data()

    # ---------- Private Helpers ----------

    def __find_by_phone(self, phone: str) -> Contact | None:
        """Returns a contact matching the phone number, or None if not found."""
        for contact in self.__contacts:
            if contact.get_phone() == phone:
                return contact
        return None

    @staticmethod
    def __validate_email(email: str) -> bool:
        """Basic regex check to catch obviously invalid email formats."""
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w{2,}$"
        return bool(re.match(pattern, email))

    @staticmethod
    def __validate_phone(phone: str) -> bool:
        """Allows digits, spaces, dashes, parentheses, and a leading +."""
        pattern = r"^\+?[\d\s\-\(\)]{7,15}$"
        return bool(re.match(pattern, phone))

    def __load_sample_data(self):
        """
        Loads hardcoded demo contacts on startup.
        This simulates a pre-populated database for demonstration purposes.
        """
        samples = [
            Contact("Ali Hassan",      "+92 300 1234567", "ali.hassan@gmail.com",    "Family"),
            Contact("Sara Ahmed",      "+92 321 9876543", "sara.ahmed@work.com",     "Work"),
            Contact("Bilal Khan",      "+92 333 5551234", "bilal.k@hotmail.com",     "Friends"),
            Contact("Zara Malik",      "+92 311 7778888", "zara.malik@yahoo.com",    "Family"),
            Contact("Usman Tariq",     "+92 345 2223333", "usman.t@company.pk",      "Work"),
            Contact("Hina Qureshi",    "+92 301 4445556", "hina.q@gmail.com",        "Friends"),
            Contact("Dr. Naveed",      "+92 321 6667778", "dr.naveed@hospital.com",  "General"),
            Contact("Maryam Siddiqui", "+92 333 9990001", "maryam.s@edu.pk",        "Work"),
        ]
        for contact in samples:
            self.__contacts.append(contact)

    # ---------- Public Methods (the PhoneBook API) ----------

    def add_contact(self, name: str, phone: str, email: str, category: str) -> dict:
        """
        Validates inputs and adds a new Contact to the phone book.
        Returns a result dict with success/error status.
        """
        # --- Field presence check ---
        if not name or not phone or not email or not category:
            return {"success": False, "error": "All fields are required."}

        # --- Category validation ---
        if category not in self.VALID_CATEGORIES:
            return {"success": False, "error": f"Invalid category. Choose from: {', '.join(self.VALID_CATEGORIES)}"}

        # --- Phone format validation ---
        if not self.__validate_phone(phone):
            return {"success": False, "error": "Invalid phone number format."}

        # --- Email format validation ---
        if not self.__validate_email(email):
            return {"success": False, "error": "Invalid email address format."}

        # --- Duplicate phone check ---
        if self.__find_by_phone(phone):
            return {"success": False, "error": f"Phone number '{phone}' is already registered."}

        # --- All checks passed: create and store ---
        new_contact = Contact(name, phone, email, category)
        self.__contacts.append(new_contact)
        return {"success": True, "message": f"Contact '{name}' added successfully.", "contact": new_contact.to_dict()}

    def delete_contact(self, phone: str) -> dict:
        """
        Deletes a contact by phone number (unique identifier).
        Returns success or error.
        """
        contact = self.__find_by_phone(phone)
        if not contact:
            return {"success": False, "error": f"No contact with phone '{phone}' found."}

        self.__contacts.remove(contact)
        return {"success": True, "message": f"Contact '{contact.get_name()}' deleted."}

    def search_contacts(self, query: str) -> list[dict]:
        """
        Searches contacts by name, phone, email, or category.
        Case-insensitive. Returns a list of matching contact dicts.
        """
        query = query.lower().strip()
        if not query:
            return self.get_all_contacts()

        results = []
        for c in self.__contacts:
            if (query in c.get_name().lower()     or
                query in c.get_phone().lower()    or
                query in c.get_email().lower()    or
                query in c.get_category().lower()):
                results.append(c.to_dict())
        return results

    def get_all_contacts(self) -> list[dict]:
        """Returns all contacts serialized as a list of dicts."""
        return [c.to_dict() for c in self.__contacts]

    def count(self) -> int:
        """Returns the total number of contacts stored."""
        return len(self.__contacts)


# =============================================================================
# Flask App Setup
# One PhoneBook instance shared across all requests (in-memory store)
# =============================================================================
phone_book = PhoneBook()


# =============================================================================
# ROUTES — JSON API Endpoints
# =============================================================================

@app.route("/")
def index():
    """Serves the main single-page UI."""
    return render_template("phonebook.html")


@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    """Returns all contacts as JSON."""
    return jsonify({
        "contacts": phone_book.get_all_contacts(),
        "count":    phone_book.count()
    })


@app.route("/api/contacts/add", methods=["POST"])
def add_contact():
    """Receives form data and adds a contact via the PhoneBook OOP class."""
    data     = request.get_json()
    name     = data.get("name", "")
    phone    = data.get("phone", "")
    email    = data.get("email", "")
    category = data.get("category", "")

    result = phone_book.add_contact(name, phone, email, category)
    status = 200 if result["success"] else 400
    result["count"] = phone_book.count()
    return jsonify(result), status


@app.route("/api/contacts/delete", methods=["DELETE"])
def delete_contact():
    """Deletes a contact by phone number."""
    data  = request.get_json()
    phone = data.get("phone", "")

    result = phone_book.delete_contact(phone)
    status = 200 if result["success"] else 404
    result["count"] = phone_book.count()
    return jsonify(result), status


@app.route("/api/contacts/search", methods=["GET"])
def search_contacts():
    """Searches contacts by a query string passed as ?q=..."""
    query   = request.args.get("q", "")
    results = phone_book.search_contacts(query)
    return jsonify({
        "contacts": results,
        "count":    phone_book.count()
    })


# =============================================================================
# Entry Point
# =============================================================================
if __name__ == "__main__":
    # debug=True for local development; set to False before deploying
    app.run(debug=True, port=5000)
