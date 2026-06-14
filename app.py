import re
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

class Contact:
    """
    Represents an individual contact entity.
    """
    def __init__(self, name: str, phone: str, email: str, category: str):
        self.name = name.strip()
        self.phone = phone.strip()
        self.email = email.strip()
        self.category = category.strip()

    def to_dict(self) -> dict:
        """
        Serializes the Contact instance into a dictionary.
        """
        return {
            "name": self.name,
            "phone": self.phone,
            "email": self.email,
            "category": self.category
        }


class PhoneBook:
    """
    Manages a collection of Contact entities using encapsulated storage.
    """
    def __init__(self):
        # Using a dictionary with phone numbers as unique keys for O(1) lookups
        self._contacts = {}

    def add_contact(self, contact: Contact) -> None:
        """
        Adds a contact. Raises ValueError if the phone number already exists.
        """
        if contact.phone in self._contacts:
            raise ValueError(f"A contact with phone number {contact.phone} already exists.")
        self._contacts[contact.phone] = contact

    def delete_contact(self, phone: str) -> bool:
        """
        Deletes a contact by phone number. Returns True if deleted, False if not found.
        """
        phone_clean = phone.strip()
        if phone_clean in self._contacts:
            del self._contacts[phone_clean]
            return True
        return False

    def get_all_contacts(self) -> list:
        """
        Returns all contact dictionaries in the system.
        """
        return [contact.to_dict() for contact in self._contacts.values()]

    def search_contacts(self, query: str) -> list:
        """
        Performs a case-insensitive search across name, phone, email, and category.
        """
        query = query.strip().lower()
        if not query:
            return self.get_all_contacts()

        results = []
        for contact in self._contacts.values():
            if (query in contact.name.lower() or
                query in contact.phone.lower() or
                query in contact.email.lower() or
                query in contact.category.lower()):
                results.append(contact.to_dict())
        return results

    def load_sample_data(self) -> None:
        """
        Loads initial mock data on system startup.
        """
        samples = [
            Contact("Jane Doe", "555-0199", "jane.doe@example.com", "Family"),
            Contact("Alex Smith", "555-0142", "alex.smith@workplace.com", "Work"),
            Contact("Emily Watson", "555-0177", "emily.w@domain.com", "Friends"),
            Contact("Robert Johnson", "555-0155", "r.johnson@general.org", "General")
        ]
        for sample in samples:
            try:
                self.add_contact(sample)
            except ValueError:
                pass


# Instantiate the global phonebook instance and load sample data
phonebook = PhoneBook()
phonebook.load_sample_data()

# --- INPUT VALIDATION HELPERS ---

def validate_contact_payload(data: dict) -> tuple:
    """
    Validates post request payloads. Returns (is_valid, error_message).
    """
    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    email = data.get("email", "").strip()
    category = data.get("category", "").strip()

    if not name or not phone or not email or not category:
        return False, "All fields (Name, Phone, Email, Category) are required."

    # Validate phone format: numbers, spaces, dashes, parentheses allowed
    if not re.match(r"^[0-9\-\+\s\(\)]+$", phone):
        return False, "Phone number contains invalid characters."

    # Validate email simple pattern
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return False, "Invalid email format."

    valid_categories = {"Family", "Work", "Friends", "General"}
    if category not in valid_categories:
        return False, "Invalid category selection."

    return True, ""


# --- FLASK ROUTING ENDPOINTS ---

@app.route("/")
def index():
    """
    Renders the single-page application dashboard.
    """
    return render_template("phonebook.html")


@app.route("/api/contacts", methods=["GET"])
def get_contacts():
    """
    Endpoint to retrieve contacts. Supports an optional search filter query string parameter 'q'.
    """
    query = request.args.get("q", "")
    if query:
        results = phonebook.search_contacts(query)
    else:
        results = phonebook.get_all_contacts()
    return jsonify(results), 200


@app.route("/api/contacts", methods=["POST"])
def add_contact():
    """
    Endpoint to add a new contact to the phonebook.
    """
    data = request.get_json() or {}
    
    # Validation step
    is_valid, error_msg = validate_contact_payload(data)
    if not is_valid:
        return jsonify({"success": False, "error": error_msg}), 400

    try:
        new_contact = Contact(
            name=data["name"],
            phone=data["phone"],
            email=data["email"],
            category=data["category"]
        )
        phonebook.add_contact(new_contact)
        return jsonify({"success": True, "message": "Contact added successfully."}), 201
    except ValueError as e:
        return jsonify({"success": False, "error": str(e)}), 400


@app.route("/api/contacts/<string:phone>", methods=["DELETE"])
def delete_contact(phone):
    """
    Endpoint to remove an existing contact by phone number.
    """
    success = phonebook.delete_contact(phone)
    if success:
        return jsonify({"success": True, "message": "Contact deleted successfully."}), 200
    return jsonify({"success": False, "error": "Contact not found."}), 404


if __name__ == "__main__":
    app.run(debug=True, port=5000)
