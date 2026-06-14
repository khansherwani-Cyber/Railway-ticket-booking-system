# Smart Phone Book — University OOP Project

A full-stack Python OOP + Flask + HTML/JS phonebook app.

## Project Structure

```
smart-phonebook/
├── app.py                  ← Python Flask backend (OOP core)
├── templates/
│   └── phonebook.html      ← Frontend UI (Bootstrap + AJAX)
├── requirements.txt        ← Python dependencies
├── vercel.json             ← Vercel deployment config
└── README.md
```

## Run Locally

```bash
# 1. Install Flask
pip install flask

# 2. Start the server
python app.py

# 3. Open your browser
# http://localhost:5000
```

## Deploy to Vercel (Free)

```bash
# 1. Install Vercel CLI (one-time)
npm install -g vercel

# 2. Login
vercel login

# 3. Deploy from the project folder
cd smart-phonebook
vercel

# Follow the prompts — Vercel auto-detects Python.
# Your live URL will appear once deployment finishes.
```

> Note: Vercel runs serverless functions, so the in-memory
> contact list resets on each cold start. This is fine for a
> university demo. For persistence, add a database (e.g. SQLite
> via Vercel Postgres or a free Supabase instance).

## OOP Classes

| Class       | Purpose                                      |
|-------------|----------------------------------------------|
| `Contact`   | Represents one contact (name, phone, email, category) |
| `PhoneBook` | Manages the list — add, delete, search, validate |

## API Endpoints

| Method   | Route                   | Action              |
|----------|-------------------------|---------------------|
| GET      | `/`                     | Serve the HTML page |
| GET      | `/api/contacts`         | Get all contacts    |
| POST     | `/api/contacts/add`     | Add a contact       |
| DELETE   | `/api/contacts/delete`  | Delete by phone     |
| GET      | `/api/contacts/search?q=` | Search contacts  |
