# BookLoop - Book Reuse & Rental Platform

A simple web application that allows users to share, rent, and sell books within their community and reduce resource wastage.

## Project Goal

BookLoop is a student-designed project addressing inefficiencies in educational resource usage, particularly in the Indian context, where millions of students struggle with textbook affordability. The project originated from observing unused competitive exam books on shelves, while peers couldn't access the same materials due to rising costs.
This early-stage initiative focuses on:

Addressing affordability - Enable students to access textbooks without a financial burden.

Short-term usage solutions - Books needed only for exams or single semesters can be borrowed.

Curriculum continuity - School students can use slightly older editions instead of buying new books for minor curriculum updates.

Reducing paper waste - Maximize utilization of existing books instead of buying new ones.

Equal access to education - Bridge the gap between students who can and cannot afford learning resources.

Local-first approach - Connect students within communities for peer-to-peer book sharing.

Thoughtful design - Focus on scalability and sustainability rather than just a finished product.

## Tech Stack

**Backend:**
- Python 3.7+
- Flask (Web Framework)
- SQLite (Database)
- JWT (Authentication)

**Frontend:**
- HTML5
- CSS3
- JavaScript (ES6+)

## Features

- User registration and login
- Add books for rent or sale
- Browse available books
- Search books by title or author
- Send book requests to owners
- Manage your book collection

## Installation

### 1. Backend Setup

Navigate to backend folder:
```bash
cd backend
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Start the server:
```bash
python app.py
```

Server will run at `http://localhost:5000`

### 2. Frontend Setup

Navigate to frontend folder:
```bash
cd frontend
```

Start local server:
```bash
python -m http.server 8000
```

Open a browser and go to `http://localhost:8000`

## Usage

1. **Register** - Create a new account with username, email, password, and location
2. **Login** - Sign in with your credentials
3. **Add Books** - Go to "My Books" tab and click "+ Add Book"
4. **Browse Books** - View all available books in the "Browse Books" tab
5. **Request Books** - Click "Request Book" to rent or buy from owners

## Project Structure

```
bookloop/
├── backend/
│   ├── app.py              # Flask API
│   ├── requirements.txt    # Dependencies
│   └── bookshare.db        # SQLite database
├── frontend/
│   ├── index.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # Main dashboard
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── dashboard.js
└── README.md
```

## API Endpoints

**Authentication:**
- `POST /api/register` - Register new user
- `POST /api/login` - Login user

**Books:**
- `GET /api/books` - Get all books
- `GET /api/books/my` - Get the user's books
- `POST /api/books` - Add new book
- `DELETE /api/books/<id>` - Delete book

**Requests:**
- `POST /api/requests` - Send book request

## Troubleshooting

**Backend won't start:**
- Make sure Python 3.7+ is installed
- Install dependencies: `pip install -r requirements.txt`

**Frontend shows errors:**
- Use `python -m http.server 8000` instead of opening HTML directly
- Make sure backend is running on port 5000

**Can't log in after registration:**
- Check browser console (F12) for errors
- Verify backend is running
- Try clearing browser cache

## Future Improvements

- In-app messaging for transaction logistics
- Email notifications
- User ratings and reviews
- Image uploads for books
- Advanced search filters
- Mobile app
   
