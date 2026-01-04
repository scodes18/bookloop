from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
CORS(app)

# Database initialization
def init_db():
    conn = sqlite3.connect('bookshare.db')
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            location TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Books table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            condition TEXT NOT NULL,
            availability_type TEXT NOT NULL,
            rent_price INTEGER,
            sale_price INTEGER,
            description TEXT,
            location TEXT NOT NULL,
            is_available INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users (user_id)
        )
    ''')
    
    # Requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            requester_id INTEGER NOT NULL,
            request_type TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (book_id) REFERENCES books (book_id),
            FOREIGN KEY (requester_id) REFERENCES users (user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Database helper
def get_db():
    conn = sqlite3.connect('bookshare.db')
    conn.row_factory = sqlite3.Row
    return conn

# JWT token decorator
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'success': False, 'message': 'Token is missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'success': False, 'message': 'Token is invalid'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated

# ============ AUTH ROUTES ============

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    location = data.get('location')
    
    if not all([username, email, password, location]):
        return jsonify({'success': False, 'message': 'All fields are required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if email already exists
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'Email already registered'}), 400
    
    # Hash password and insert user
    password_hash = generate_password_hash(password)
    cursor.execute(
        'INSERT INTO users (username, email, password_hash, location) VALUES (?, ?, ?, ?)',
        (username, email, password_hash, location)
    )
    conn.commit()
    
    user_id = cursor.lastrowid
    conn.close()
    
    # Generate token
    token = jwt.encode({
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'message': 'Registration successful',
        'token': token,
        'user': {
            'user_id': user_id,
            'username': username,
            'email': email,
            'location': location
        }
    }), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    
    email = data.get('email')
    password = data.get('password')
    
    if not all([email, password]):
        return jsonify({'success': False, 'message': 'Email and password required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
    
    # Generate token
    token = jwt.encode({
        'user_id': user['user_id'],
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
    }, app.config['SECRET_KEY'], algorithm='HS256')
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'token': token,
        'user': {
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'location': user['location']
        }
    }), 200

# ============ BOOK ROUTES ============

@app.route('/api/books', methods=['GET'])
def get_books():
    conn = get_db()
    cursor = conn.cursor()
    
    # Get all available books with owner information
    cursor.execute('''
        SELECT b.*, u.username as owner_name, u.location as owner_location
        FROM books b
        JOIN users u ON b.owner_id = u.user_id
        WHERE b.is_available = 1
        ORDER BY b.created_at DESC
    ''')
    
    books = cursor.fetchall()
    conn.close()
    
    books_list = []
    for book in books:
        books_list.append({
            'id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'condition': book['condition'],
            'availabilityType': book['availability_type'],
            'rentPrice': book['rent_price'],
            'salePrice': book['sale_price'],
            'description': book['description'],
            'location': book['location'],
            'owner': book['owner_name'],
            'ownerId': book['owner_id']
        })
    
    return jsonify({'success': True, 'books': books_list}), 200

@app.route('/api/books/my', methods=['GET'])
@token_required
def get_my_books(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM books
        WHERE owner_id = ?
        ORDER BY created_at DESC
    ''', (current_user_id,))
    
    books = cursor.fetchall()
    conn.close()
    
    books_list = []
    for book in books:
        books_list.append({
            'id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'condition': book['condition'],
            'availabilityType': book['availability_type'],
            'rentPrice': book['rent_price'],
            'salePrice': book['sale_price'],
            'description': book['description'],
            'location': book['location'],
            'isAvailable': bool(book['is_available'])
        })
    
    return jsonify({'success': True, 'books': books_list}), 200

@app.route('/api/books', methods=['POST'])
@token_required
def add_book(current_user_id):
    data = request.get_json()
    
    title = data.get('title')
    author = data.get('author')
    condition = data.get('condition')
    availability_type = data.get('availabilityType')
    rent_price = data.get('rentPrice')
    sale_price = data.get('salePrice')
    description = data.get('description')
    location = data.get('location')
    
    if not all([title, author, condition, availability_type, location]):
        return jsonify({'success': False, 'message': 'Required fields missing'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO books (owner_id, title, author, condition, availability_type,
                          rent_price, sale_price, description, location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (current_user_id, title, author, condition, availability_type,
          rent_price, sale_price, description, location))
    
    book_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Book added successfully',
        'book_id': book_id
    }), 201

@app.route('/api/books/<int:book_id>', methods=['PUT'])
@token_required
def update_book(current_user_id, book_id):
    data = request.get_json()
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if book belongs to user
    cursor.execute('SELECT * FROM books WHERE book_id = ? AND owner_id = ?',
                   (book_id, current_user_id))
    book = cursor.fetchone()
    
    if not book:
        conn.close()
        return jsonify({'success': False, 'message': 'Book not found or unauthorized'}), 404
    
    # Update book
    cursor.execute('''
        UPDATE books
        SET title = ?, author = ?, condition = ?, availability_type = ?,
            rent_price = ?, sale_price = ?, description = ?, is_available = ?
        WHERE book_id = ?
    ''', (data.get('title'), data.get('author'), data.get('condition'),
          data.get('availabilityType'), data.get('rentPrice'), data.get('salePrice'),
          data.get('description'), data.get('isAvailable', 1), book_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Book updated successfully'}), 200

@app.route('/api/books/<int:book_id>', methods=['DELETE'])
@token_required
def delete_book(current_user_id, book_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM books WHERE book_id = ? AND owner_id = ?',
                   (book_id, current_user_id))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'success': False, 'message': 'Book not found or unauthorized'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Book deleted successfully'}), 200

# ============ REQUEST ROUTES ============

@app.route('/api/requests', methods=['POST'])
@token_required
def create_request(current_user_id):
    data = request.get_json()
    
    book_id = data.get('bookId')
    request_type = data.get('requestType')
    message = data.get('message')
    
    if not all([book_id, request_type, message]):
        return jsonify({'success': False, 'message': 'All fields required'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if book exists
    cursor.execute('SELECT * FROM books WHERE book_id = ?', (book_id,))
    book = cursor.fetchone()
    
    if not book:
        conn.close()
        return jsonify({'success': False, 'message': 'Book not found'}), 404
    
    # Create request
    cursor.execute('''
        INSERT INTO requests (book_id, requester_id, request_type, message)
        VALUES (?, ?, ?, ?)
    ''', (book_id, current_user_id, request_type, message))
    
    request_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Request sent successfully',
        'request_id': request_id
    }), 201

@app.route('/api/requests/received', methods=['GET'])
@token_required
def get_received_requests(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # Get requests for books owned by current user
    cursor.execute('''
        SELECT r.*, b.title, b.author, u.username as requester_name, u.email as requester_email
        FROM requests r
        JOIN books b ON r.book_id = b.book_id
        JOIN users u ON r.requester_id = u.user_id
        WHERE b.owner_id = ?
        ORDER BY r.created_at DESC
    ''', (current_user_id,))
    
    requests = cursor.fetchall()
    conn.close()
    
    requests_list = []
    for req in requests:
        requests_list.append({
            'requestId': req['request_id'],
            'bookId': req['book_id'],
            'bookTitle': req['title'],
            'bookAuthor': req['author'],
            'requesterName': req['requester_name'],
            'requesterEmail': req['requester_email'],
            'requestType': req['request_type'],
            'message': req['message'],
            'status': req['status'],
            'createdAt': req['created_at']
        })
    
    return jsonify({'success': True, 'requests': requests_list}), 200

@app.route('/api/requests/sent', methods=['GET'])
@token_required
def get_sent_requests(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT r.*, b.title, b.author, u.username as owner_name, u.email as owner_email
        FROM requests r
        JOIN books b ON r.book_id = b.book_id
        JOIN users u ON b.owner_id = u.user_id
        WHERE r.requester_id = ?
        ORDER BY r.created_at DESC
    ''', (current_user_id,))
    
    requests = cursor.fetchall()
    conn.close()
    
    requests_list = []
    for req in requests:
        requests_list.append({
            'requestId': req['request_id'],
            'bookId': req['book_id'],
            'bookTitle': req['title'],
            'bookAuthor': req['author'],
            'ownerName': req['owner_name'],
            'ownerEmail': req['owner_email'],
            'requestType': req['request_type'],
            'message': req['message'],
            'status': req['status'],
            'createdAt': req['created_at']
        })
    
    return jsonify({'success': True, 'requests': requests_list}), 200

@app.route('/api/requests/<int:request_id>/status', methods=['PUT'])
@token_required
def update_request_status(current_user_id, request_id):
    data = request.get_json()
    status = data.get('status')
    
    if status not in ['approved', 'rejected', 'completed']:
        return jsonify({'success': False, 'message': 'Invalid status'}), 400
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Check if user owns the book
    cursor.execute('''
        SELECT r.* FROM requests r
        JOIN books b ON r.book_id = b.book_id
        WHERE r.request_id = ? AND b.owner_id = ?
    ''', (request_id, current_user_id))
    
    req = cursor.fetchone()
    
    if not req:
        conn.close()
        return jsonify({'success': False, 'message': 'Request not found or unauthorized'}), 404
    
    cursor.execute('UPDATE requests SET status = ? WHERE request_id = ?',
                   (status, request_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Request status updated'}), 200

# ============ SEARCH ROUTE ============

@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = request.args.get('q', '')
    filter_type = request.args.get('filter', 'all')
    
    conn = get_db()
    cursor = conn.cursor()
    
    sql = '''
        SELECT b.*, u.username as owner_name
        FROM books b
        JOIN users u ON b.owner_id = u.user_id
        WHERE b.is_available = 1
        AND (b.title LIKE ? OR b.author LIKE ?)
    '''
    
    params = [f'%{query}%', f'%{query}%']
    
    if filter_type != 'all':
        sql += ' AND (b.availability_type = ? OR b.availability_type = "both")'
        params.append(filter_type)
    
    sql += ' ORDER BY b.created_at DESC'
    
    cursor.execute(sql, params)
    books = cursor.fetchall()
    conn.close()
    
    books_list = []
    for book in books:
        books_list.append({
            'id': book['book_id'],
            'title': book['title'],
            'author': book['author'],
            'condition': book['condition'],
            'availabilityType': book['availability_type'],
            'rentPrice': book['rent_price'],
            'salePrice': book['sale_price'],
            'description': book['description'],
            'location': book['location'],
            'owner': book['owner_name']
        })
    
    return jsonify({'success': True, 'books': books_list}), 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)