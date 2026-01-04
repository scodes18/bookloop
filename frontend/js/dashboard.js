const API_BASE = 'http://localhost:5000/api';
let currentUser = null;
let authToken = null;
let allBooks = [];
let myBooks = [];

// Check authentication on page load
window.onload = function() {
    authToken = localStorage.getItem('authToken');
    const savedUser = localStorage.getItem('currentUser');
    
    if (!authToken || !savedUser) {
        window.location.href = 'index.html';
        return;
    }
    
    currentUser = JSON.parse(savedUser);
    document.getElementById('userNameDisplay').textContent = currentUser.username;
    
    loadBooks();
};

// Tab switching
function showTab(tab) {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');

    const browseTab = document.getElementById('browseTab');
    const mybooksTab = document.getElementById('mybooksTab');

    if (tab === 'browse') {
        browseTab.classList.remove("hidden");
        mybooksTab.classList.add("hidden");
        loadBooks();
    } else {
        browseTab.classList.add("hidden");
        mybooksTab.classList.remove("hidden");
        loadMyBooks();
    }
}

// Load all available books
async function loadBooks() {
    try {
        const response = await fetch(`${API_BASE}/books`);
        const data = await response.json();
        
        if (data.success) {
            allBooks = data.books;
            renderBooks();
        }
    } catch (error) {
        console.error('Error loading books:', error);
        alert('Failed to load books. Make sure backend is running.');
    }
}

// Load user's books
async function loadMyBooks() {
    try {
        const response = await fetch(`${API_BASE}/books/my`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            myBooks = data.books;
            renderMyBooks();
        }
    } catch (error) {
        console.error('Error loading my books:', error);
    }
}

// Filter books
function filterBooks() {
    const searchInput = document.getElementById('searchInput');
    const q = searchInput.value.toLowerCase();
    const filtered = allBooks.filter(
        b => b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q)
    );
    renderBooks(filtered);
}

// Render browse books
function renderBooks(books = allBooks) {
    const booksGrid = document.getElementById('booksGrid');
    booksGrid.innerHTML = "";
    
    if (books.length === 0) {
        booksGrid.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">No books found</p>';
        return;
    }
    
    books.forEach(b => {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <h3>${b.title}</h3>
            <p style="color: #666; margin-bottom: 8px;">by ${b.author}</p>
            <p style="font-size: 13px; color: #999; margin-bottom: 12px;">
                <span>📍</span> ${b.location} • <span>👤</span> ${b.owner}
            </p>
            <div style="display: flex; gap: 10px; margin-bottom: 12px;">
                ${b.rentPrice ? `
                    <div style="flex: 1; background: #e3f2fd; padding: 8px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #1976d2; font-weight: 600;">RENT</div>
                        <div style="font-size: 16px; color: #1565c0; font-weight: 700;">₹${b.rentPrice}</div>
                    </div>
                ` : ''}
                ${b.salePrice ? `
                    <div style="flex: 1; background: #e8f5e9; padding: 8px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #388e3c; font-weight: 600;">BUY</div>
                        <div style="font-size: 16px; color: #2e7d32; font-weight: 700;">₹${b.salePrice}</div>
                    </div>
                ` : ''}
            </div>
            <button onclick="showRequestModal(${b.id})" style="width: 100%; padding: 10px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
                Request Book
            </button>
        `;
        booksGrid.appendChild(card);
    });
}

// Render my books
function renderMyBooks() {
    const myBooksGrid = document.getElementById('myBooksGrid');
    myBooksGrid.innerHTML = "";
    
    if (myBooks.length === 0) {
        myBooksGrid.innerHTML = '<p style="text-align: center; padding: 40px; color: #666;">No books added yet. Click "+ Add Book" to list your first book!</p>';
        return;
    }
    
    myBooks.forEach(b => {
        const card = document.createElement('div');
        card.className = 'book-card';
        card.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <div>
                    <h3>${b.title}</h3>
                    <p style="color: #666;">by ${b.author}</p>
                </div>
                <span style="padding: 4px 10px; border-radius: 12px; font-size: 11px; font-weight: 600; ${
                    b.isAvailable 
                        ? 'background: #4caf50; color: white;' 
                        : 'background: #e0e0e0; color: #666;'
                }">
                    ${b.isAvailable ? 'Available' : 'Rented'}
                </span>
            </div>
            <p style="font-size: 13px; color: #999; margin-bottom: 12px;">
                Condition: ${b.condition}
            </p>
            <div style="display: flex; gap: 10px; margin-bottom: 12px;">
                ${b.rentPrice ? `
                    <div style="flex: 1; background: #e3f2fd; padding: 8px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #1976d2;">RENT</div>
                        <div style="font-size: 14px; color: #1565c0; font-weight: 700;">₹${b.rentPrice}</div>
                    </div>
                ` : ''}
                ${b.salePrice ? `
                    <div style="flex: 1; background: #e8f5e9; padding: 8px; border-radius: 8px; text-align: center;">
                        <div style="font-size: 11px; color: #388e3c;">SALE</div>
                        <div style="font-size: 14px; color: #2e7d32; font-weight: 700;">₹${b.salePrice}</div>
                    </div>
                ` : ''}
            </div>
            <button onclick="deleteBook(${b.id})" style="width: 100%; padding: 10px; background: #f44336; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: 600;">
                Delete Book
            </button>
        `;
        myBooksGrid.appendChild(card);
    });
}

// Request Modal
let selectedBookForRequest = null;

function showRequestModal(bookId) {
    selectedBookForRequest = allBooks.find(b => b.id === bookId);
    
    if (!selectedBookForRequest) return;
    
    const modal = document.createElement('div');
    modal.id = 'requestModal';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000;';
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; padding: 30px; width: 90%; max-width: 500px;">
            <h2 style="margin-bottom: 20px;">Request Book</h2>
            <div style="margin-bottom: 20px;">
                <h3 style="font-size: 18px; margin-bottom: 5px;">${selectedBookForRequest.title}</h3>
                <p style="color: #666;">by ${selectedBookForRequest.author}</p>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; font-weight: 600; margin-bottom: 8px;">Request Type</label>
                <select id="requestType" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;">
                    ${selectedBookForRequest.rentPrice ? `<option value="rent">Rent (₹${selectedBookForRequest.rentPrice})</option>` : ''}
                    ${selectedBookForRequest.salePrice ? `<option value="buy">Buy (₹${selectedBookForRequest.salePrice})</option>` : ''}
                </select>
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; font-weight: 600; margin-bottom: 8px;">Message to Owner</label>
                <textarea id="requestMessage" rows="4" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;" placeholder="Introduce yourself..."></textarea>
            </div>
            
            <div style="display: flex; gap: 15px;">
                <button onclick="sendRequest()" style="flex: 1; padding: 12px; background: #667eea; color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer;">
                    Send Request
                </button>
                <button onclick="closeRequestModal()" style="flex: 1; padding: 12px; background: #e0e0e0; color: #666; border: none; border-radius: 10px; font-weight: 600; cursor: pointer;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeRequestModal() {
    const modal = document.getElementById('requestModal');
    if (modal) modal.remove();
    selectedBookForRequest = null;
}

async function sendRequest() {
    const requestType = document.getElementById('requestType').value;
    const message = document.getElementById('requestMessage').value;
    
    if (!message.trim()) {
        alert('Please enter a message');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/requests`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                bookId: selectedBookForRequest.id,
                requestType: requestType,
                message: message
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Request sent successfully!');
            closeRequestModal();
        } else {
            alert(data.message || 'Failed to send request');
        }
    } catch (error) {
        console.error('Error sending request:', error);
        alert('Failed to send request. Please try again.');
    }
}

// Add Book Modal
function showAddBookModal() {
    const modal = document.createElement('div');
    modal.id = 'addBookModal';
    modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 1000; padding: 20px;';
    
    modal.innerHTML = `
        <div style="background: white; border-radius: 20px; padding: 30px; width: 100%; max-width: 500px; max-height: 90vh; overflow-y: auto;">
            <h2 style="margin-bottom: 20px;">Add New Book</h2>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; font-weight: 600; margin-bottom: 6px;">Title *</label>
                <input type="text" id="addBookTitle" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; font-weight: 600; margin-bottom: 6px;">Author *</label>
                <input type="text" id="addBookAuthor" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; font-weight: 600; margin-bottom: 6px;">Condition *</label>
                <select id="addBookCondition" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;">
                    <option>New</option>
                    <option>Like New</option>
                    <option>Good</option>
                    <option>Fair</option>
                </select>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; font-weight: 600; margin-bottom: 6px;">Availability *</label>
                <select id="addBookAvailability" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;">
                    <option value="both">Rent & Sale</option>
                    <option value="rent">Rent Only</option>
                    <option value="sale">Sale Only</option>
                </select>
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; font-weight: 600; margin-bottom: 6px;">Rent Price (₹)</label>
                <input type="number" id="addBookRentPrice" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; font-weight: 600; margin-bottom: 6px;">Sale Price (₹)</label>
                <input type="number" id="addBookSalePrice" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;">
            </div>
            
            <div style="margin-bottom: 20px;">
                <label style="display: block; font-weight: 600; margin-bottom: 6px;">Description</label>
                <textarea id="addBookDescription" rows="3" style="width: 100%; padding: 10px; border: 2px solid #e0e0e0; border-radius: 10px;"></textarea>
            </div>
            
            <div style="display: flex; gap: 15px;">
                <button onclick="addBook()" style="flex: 1; padding: 12px; background: #667eea; color: white; border: none; border-radius: 10px; font-weight: 600; cursor: pointer;">
                    Add Book
                </button>
                <button onclick="closeAddBookModal()" style="flex: 1; padding: 12px; background: #e0e0e0; color: #666; border: none; border-radius: 10px; font-weight: 600; cursor: pointer;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function closeAddBookModal() {
    const modal = document.getElementById('addBookModal');
    if (modal) modal.remove();
}

async function addBook() {
    const title = document.getElementById('addBookTitle').value;
    const author = document.getElementById('addBookAuthor').value;
    const condition = document.getElementById('addBookCondition').value;
    const availabilityType = document.getElementById('addBookAvailability').value;
    const rentPrice = document.getElementById('addBookRentPrice').value;
    const salePrice = document.getElementById('addBookSalePrice').value;
    const description = document.getElementById('addBookDescription').value;
    
    if (!title || !author) {
        alert('Please fill in required fields (Title and Author)');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/books`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${authToken}`
            },
            body: JSON.stringify({
                title,
                author,
                condition,
                availabilityType,
                rentPrice: rentPrice ? parseInt(rentPrice) : null,
                salePrice: salePrice ? parseInt(salePrice) : null,
                description,
                location: currentUser.location
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Book added successfully!');
            closeAddBookModal();
            loadMyBooks();
        } else {
            alert(data.message || 'Failed to add book');
        }
    } catch (error) {
        console.error('Error adding book:', error);
        alert('Failed to add book. Please try again.');
    }
}

async function deleteBook(bookId) {
    if (!confirm('Are you sure you want to delete this book?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/books/${bookId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('Book deleted successfully!');
            loadMyBooks();
        } else {
            alert(data.message || 'Failed to delete book');
        }
    } catch (error) {
        console.error('Error deleting book:', error);
        alert('Failed to delete book. Please try again.');
    }
}

function handleLogout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('currentUser');
        window.location.href = 'index.html';
    }
}