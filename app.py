from flask import Flask, render_template, request, redirect, url_for, session, Response, jsonify
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge
import MySQLdb.cursors
import re
import os
import sys

app = Flask(__name__)
app.secret_key = 'your_secret_key'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'mysql'
app.config['MYSQL_DB'] = 'library'
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Set to 5 megabytes
  
mysql = MySQL(app)

@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    # Determine the current endpoint
    current_endpoint = request.endpoint

    # Decide which template to render based on the endpoint
    if current_endpoint == 'FormAddBooks':
        return render_template('FormAddBooks.html', message="File too large", is_file_too_large=True), 413
    elif current_endpoint == 'editBook':  # Replace 'editBook' with your actual edit book endpoint name
        return render_template('editBook.html', message="File too large", is_file_too_large=True), 413
    else:
        # Default response if the endpoint is neither
        return 'File too large', 413
    

@app.route('/index')
def index():
    # Check if user is logged in and either a Librarian or a Patron
    if 'loggedin' in session and session['user_type'] in ['Librarian', 'Patron']:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM books")  # Adjust the query as needed
        books = cursor.fetchall()
        # Fetch user details from the session
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')

        return render_template('index.html', first_name=first_name, user_type=user_type, books=books)
    else:
        # Render the modified error-404 template
        return render_template('error-404.html'), 403


@app.route('/adminDashboard')
def adminDashboard():
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Query to count total books
        cursor.execute("SELECT COUNT(*) as total_books FROM Books")
        total_books = cursor.fetchone()['total_books']

        # Query to count total users
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()['total_users']

        return render_template('adminDashboard.html', total_books=total_books, total_users=total_users, first_name=first_name, user_type=user_type)
    else:
         # Render the modified error-404 template
        return render_template('error-404.html'), 403


@app.route('/listOfBooksUser')
def listOfBooksUser():
    # Check if user is logged in and either a Librarian or a Patron
    if 'loggedin' in session and session['user_type'] in ['Librarian', 'Patron']:
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        page = request.args.get('page', 1, type=int)
        items_per_page = 5
        start = (page - 1) * items_per_page

        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            # Query to get the books for the current page
            cursor.execute("SELECT EntryNumber, BookName, Author, Publisher, ISBN, LatestVersion, Shelf, Borrowed FROM Books LIMIT %s, %s", (start, items_per_page))
            rows = cursor.fetchall()

            # Query to get the total count of books
            cursor.execute("SELECT COUNT(*) FROM Books")
            total_books = cursor.fetchone()['COUNT(*)']
            total_pages = (total_books + items_per_page - 1) // items_per_page

        return render_template('listOfBooksUser.html', books=rows, total_pages=total_pages, current_page=page, first_name=first_name, user_type=user_type)
    else:
        # Render the modified error-404 template
        return render_template('error-404.html'), 403


@app.route('/search_books_user')
def search_books_user():
    # Check if user is logged in and either a Librarian or a Patron
    if 'loggedin' in session and session['user_type'] in ['Librarian', 'Patron']:
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        search_query = request.args.get('query', '')  # Get the search query from the URL parameters
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Prepare the search query for SQL LIKE statement
        search_query = f"%{search_query}%"
        
        # Construct the SQL query to search books
        search_sql = """SELECT * FROM Books WHERE 
                        BookName LIKE %s OR 
                        Author LIKE %s OR 
                        Publisher LIKE %s OR 
                        ISBN LIKE %s"""
        cursor.execute(search_sql, (search_query, search_query, search_query, search_query))
        search_results = cursor.fetchall()

        return render_template('searchBooksUser.html', search_query=search_query, search_results=search_results, first_name=first_name, user_type=user_type)
    else:
        # Render the modified error-404 template
        return render_template('error-404.html'), 403



@app.route('/searchUser')
def searchUsers():
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        return render_template('searchUser.html', first_name=first_name, user_type=user_type)
    else:
        # Render the modified error-404 template
        return render_template('error-404.html'), 403

@app.route('/searchBooks')
def searchBooks():
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        return render_template('searchBooks.html', first_name=first_name, user_type=user_type)
    else:
        # Render the modified error-404 template
        return render_template('error-404.html'), 403

@app.route('/searchBooksUser')
def searchBooksUser():
    # Check if user is logged in and either a Librarian or a Patron
    if 'loggedin' in session and session['user_type'] in ['Librarian', 'Patron']:
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        return render_template('searchBooksUser.html', first_name=first_name, user_type=user_type)
    else:
        # Render the modified error-404 template
        return render_template('error-404.html'), 403


@app.route('/error-404')
def error_404():
    return render_template('error-404.html')

@app.route('/')
# Login function
@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    login_success = False  # Add a flag for successful login
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        if user and check_password_hash(user['password'], password):
            print("Login successful, UserType:", user['UserType'])  # Debugging statement
            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['first_name']
            session['email'] = user['email']
            session['user_type'] = user['UserType']
            message = 'Logged in successfully !'
            login_success = True
            # Store the intended redirection in the session
            session['next_page'] = 'adminDashboard' if user['UserType'] == 'Librarian' else 'index'
        else:
            print("Login failed")  # Debugging statement
            message = 'Incorrect email/password!'
    # reset login_success flag when rendering the login page
    # session.pop('login_success', None)
    return render_template('login.html', message=message, login_success=login_success)

# SIGN UP FUNCTION
@app.route('/sign-up', methods=['GET', 'POST'])
def register():
    message = ''
    register_success = False  # Initialize the flag
    if request.method == 'POST':
        # Extract form data
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        email = request.form.get('email')
        UserType = request.form.get('UserType')
        registration_code = request.form.get('registration_code', '')  # Default to empty string

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Check for existing email
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not first_name or not last_name or not email:
            message = 'Please fill out the form!'
        elif len(password) > 12 or len(set(password)) == len(password):
            message = 'Password must be a maximum of 12 characters and contain at least one unique character!'
        else:
            # Check registration code for librarian
            if UserType == 'Librarian':
                if not registration_code:
                    message = 'Registration code is required for librarian sign-up!'
                    return render_template('sign-up.html', message=message)

                cursor.execute('SELECT * FROM registration_codes WHERE code = %s', (registration_code,))
                code_entry = cursor.fetchone()

                if not code_entry or code_entry['is_used']:
                    message = 'Invalid or already used registration code!'
                    return render_template('sign-up.html', message=message)

                # Mark the code as used
                cursor.execute('UPDATE registration_codes SET is_used = TRUE WHERE code = %s', (registration_code,))

            # Hashing the password before storing it
            hashed_password = generate_password_hash(password)
            cursor.execute('INSERT INTO users (first_name, last_name, email, password, UserType) VALUES (%s, %s, %s, %s, %s)', 
                           (first_name, last_name, email, hashed_password, UserType))
            mysql.connection.commit()

            # Retrieve the ID of the newly created user
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            new_user = cursor.fetchone()
            new_user_id = new_user['id']

            if UserType == 'Librarian' and registration_code:
                # Update the registration_codes table
                cursor.execute('UPDATE registration_codes SET is_used = TRUE, UsedBy = %s WHERE code = %s', 
                            (new_user_id, registration_code))
                mysql.connection.commit()

                message = 'You have successfully registered!'
                register_success = True  # Set the flag to True when registration is successful

    return render_template('sign-up.html', message=message, register_success=register_success)


@app.route('/listOfUser')
def listOfUser():
    # Check if the user is logged in and is a Librarian
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        query = "SELECT * FROM users"
        with mysql.connection.cursor() as cursor:
            cursor.execute(query)
            columns = [column[0] for column in cursor.description]
            users = [dict(zip(columns, row)) for row in cursor.fetchall()]
        return render_template('listOfUser.html', users=users, first_name = first_name, user_type = user_type)
    else:
        # Redirect to the login page or show an unauthorized access message
        return render_template('error-404.html'), 403


@app.route('/FormAddUser', methods=['GET', 'POST'])
def FormAddUser():
    # Initialize the flag and message
    message = ''
    add_user_success = False

    # Check if the user is logged in and is a Librarian
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        if request.method == 'POST':
            # Extract form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            user_type = request.form.get('UserType')

            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            # Check for existing email
            cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
            account = cursor.fetchone()

            if account:
                message = ('Account already exists!', 'error')
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                message = ('Invalid email address!', 'error')
            elif not first_name or not last_name or not password or not email:
                message = ('Please fill out the form!', 'error')
            else:
                # Hashing the password before storing it
                hashed_password = generate_password_hash(password)
                cursor.execute('INSERT INTO users (first_name, last_name, email, password, UserType) VALUES (%s, %s, %s, %s, %s)', 
                               (first_name, last_name, email, hashed_password, user_type))
                mysql.connection.commit()
                message = ('User has been successfully added!', 'success')
                add_user_success = True  # Set the flag to True when the user is successfully added

        # Render the template for GET request or after form submission
        return render_template('FormAddUser.html', message=message, add_user_success=add_user_success, first_name = first_name, user_type = user_type)
    else:
        # Redirect to the login page or show an unauthorized access message
        return render_template('error-404.html'), 403



@app.route("/EditUser/<int:userid>", methods=['GET', 'POST'])
def EditUser(userid):
    # Check if user is logged in and is a Librarian
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if request.method == 'POST':
            # Process the form submission
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            email = request.form['email']
            password = request.form.get('password')  # Get the password, it may be None
            user_type = request.form['UserType']

            if password:
                # Hash the new password if provided
                hashed_password = generate_password_hash(password)
                update_query = """UPDATE users SET first_name=%s, last_name=%s, email=%s, password=%s, UserType=%s
                                  WHERE id=%s"""
                cursor.execute(update_query, (first_name, last_name, email, hashed_password, user_type, userid))
            else:
                # Update without changing the password
                update_query = """UPDATE users SET first_name=%s, last_name=%s, email=%s, UserType=%s
                                  WHERE id=%s"""
                cursor.execute(update_query, (first_name, last_name, email, user_type, userid))

            mysql.connection.commit()
            return redirect(url_for('listOfUser'))  # Redirect to the user list page after update

        # Fetch the user to edit
        cursor.execute("SELECT * FROM users WHERE id = %s", (userid,))
        user = cursor.fetchone()

        if user:
            return render_template("EditUser.html", user=user, first_name=first_name, user_type=user_type)
        else:
            return "User not found", 404
    else:
        # Redirect to the login page or show an unauthorized access message
        return render_template('error-404.html'), 403



@app.route("/delete_user/<int:userid>", methods=['POST'])
def delete_user(userid):
    # Check if user is logged in and is a Librarian
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute('DELETE FROM users WHERE id = %s', (userid,))
            mysql.connection.commit()
            return jsonify({"success": True, "message": "User deleted successfully"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    else:
        # Return a message indicating lack of authorization
        return jsonify({"success": False, "message": "Unauthorized access"}), 403





@app.route("/password_change", methods =['GET', 'POST'])
def password_change():
    mesage = ''
    if 'loggedin' in session:
        changePassUserId = request.args.get('userid')        
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form and 'userid' in request.form  :
            password = request.form['password']   
            confirm_pass = request.form['confirm_pass'] 
            userId = request.form['userid']
            if not password or not confirm_pass:
                mesage = 'Please fill out the form !'
            elif password != confirm_pass:
                mesage = 'Confirm password is not equal!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute('UPDATE user SET  password =% s WHERE id =% s', (password, (userId, ), ))
                mysql.connection.commit()
                mesage = 'Password updated !'            
        elif request.method == 'POST':
            mesage = 'Please fill out the form !'        
        return render_template("password_change.html", mesage = mesage, changePassUserId = changePassUserId)
    return redirect(url_for('login'))   

  # LLOG OUT FUNCTION
@app.route('/logout')
def logout():
    # Clear the session
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('name', None)
    session.pop('email', None)
    session.pop('user_type', None)
    # Redirect to the login page
    return redirect(url_for('login'))

@app.route("/FormAddBooks", methods=['GET', 'POST'])
def FormAddBooks():
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        message = None  # Initialize message as None
        addBooks_success = False

        if request.method == 'POST':
            # Define maximum length constraints
            MAX_ENTRY_NUMBER_LENGTH = 10 
            MAX_ISBN_LENGTH = 15  # Typical ISBN length
            MAX_BOOK_NAME = 50 
            MAX_AUTHOR = 50  
            MAX_PUBLISHER = 40  
            MAX_LATEST_VERSION = 13  
            MAX_SHELF = 13
            
            # Extracting form data
            entry_number = request.form['EntryNumber']
            book_name = request.form['BookName']
            author = request.form['Author']
            publisher = request.form['Publisher']
            isbn = request.form['ISBN']
            latest_version = request.form['LatestVersion']
            shelf = request.form['Shelf']

            # Check lengths of each field
            if len(entry_number) > MAX_ENTRY_NUMBER_LENGTH:
                message = 'Error: Entry number is too long.'
            elif len(isbn) > MAX_ISBN_LENGTH:
                message = 'Error: ISBN is too long.'
            elif len(book_name) > MAX_BOOK_NAME:
                message = 'Error: Book Name is too long.'
            elif len(author) > MAX_AUTHOR:
                message = 'Error: Author is too long.'
            elif len(publisher) > MAX_PUBLISHER:
                message = 'Error: Publisher is too long.'
            elif len(latest_version) > MAX_LATEST_VERSION:
                message = 'Error: Latest Version is too long.'
            elif len(shelf) > MAX_SHELF:
                message = 'Error: Shelf is too long.'

            if message:  # If there's any error in length checks, return early
                return render_template('FormAddBooks.html', message=message, addBooks_success=addBooks_success, first_name=first_name, user_type=user_type)

            # Handling the cover image
            cover_image = request.files['CoverImage']
            filename = secure_filename(cover_image.filename)
            file_path = os.path.join('uploads', filename)
            cover_image.save(file_path)

            # Define the INSERT query
            query = """INSERT INTO books (EntryNumber, BookName, Author, Publisher, ISBN, LatestVersion, Shelf, CoverImage) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            try:
                with mysql.connection.cursor() as cursor:
                    # Check if a book with the same entry number or ISBN already exists
                    cursor.execute("SELECT * FROM books WHERE EntryNumber = %s OR ISBN = %s", (entry_number, isbn))
                    if cursor.fetchone():
                        # Book already exists, set error message
                        message = 'Error: Book with the same entry number or ISBN already exists.'
                        addBooks_success = False
                    else:
                        # If the book doesn't exist, insert the new book data
                        with open(file_path, 'rb') as file:
                            binary_data = file.read()
                        cursor.execute(query, (entry_number, book_name, author, publisher, isbn, latest_version, shelf, binary_data))
                        mysql.connection.commit()
                        addBooks_success = True
                        # message = 'Success: Book added successfully!'
                        # Redirect to the list of books if successful
                        # return redirect(url_for('listOfBooks'))

            except MySQLdb._exceptions.IntegrityError as e:
                # Handle specific database errors related to integrity constraints
                mysql.connection.rollback()
                message = 'Error: Book with the same entry number or ISBN already exists.'
            except MySQLdb._exceptions.DataError as e:
                # Handle specific database errors related to data issues
                mysql.connection.rollback()
                message = 'Error: Input data is too long.'
            except Exception as e:
                # Handle any other exception that occurred during database operations
                mysql.connection.rollback()
                message = f'An unexpected error occurred: {str(e)}'
            finally:
                # Close the cursor and delete the temporary file
                cursor.close()
                if os.path.exists(file_path):
                    os.remove(file_path)

        return render_template('FormAddBooks.html', message=message, addBooks_success=addBooks_success, first_name=first_name, user_type=user_type)

    else:
        return render_template('error-404.html'), 403
    
# List all of books    
@app.route('/listOfBooks')
def listOfBooks():
    if 'loggedin' in session and session['user_type'] in ['Librarian']:
        first_name = session.get('name', 'Default User')
        user_type = session.get('user_type', 'Unknown Type')
        query = """
            SELECT 
                Books.EntryNumber, 
                Books.BookName, 
                Books.Author, 
                Books.Publisher, 
                Books.ISBN, 
                Books.LatestVersion, 
                Books.Shelf, 
                Books.Borrowed,
                Books.BorrowedBy,
                CONCAT(users.first_name, ' ', users.last_name) AS BorrowerName
            FROM 
                Books
            LEFT JOIN 
                users ON Books.BorrowedBy = users.id
            """
        with mysql.connection.cursor() as cursor:
            cursor.execute(query)
            books = [dict(zip([column[0] for column in cursor.description], row)) for row in cursor.fetchall()]
        return render_template('listOfBooks.html', books=books, first_name=first_name, user_type=user_type)
    else:
        return render_template('error-404.html'), 403



# CODE TO RETRIEVE ALL THE IMAGES
@app.route('/cover_image/<int:entry_number>')
def cover_image(entry_number):
    # Check if user is logged in and either a Librarian or a Patron
    if 'loggedin' in session and session['user_type'] in ['Librarian','Patron']:
        query = "SELECT CoverImage FROM Books WHERE EntryNumber = %s"
        with mysql.connection.cursor() as cursor:
            cursor.execute(query, (entry_number,))
            cover_image_data = cursor.fetchone()[0]
            return Response(cover_image_data, mimetype='image/png')
    else:
        # Redirect to login if not logged in or if user type is not allowed
        return redirect(url_for('login'))



@app.route("/EditBooks/<int:entry_number>", methods=['GET', 'POST'])
def EditBooks(entry_number):
    # Check if user is logged in and is a Librarian
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        message = None

        if request.method == 'POST':

            # Define maximum length constraints
            MAX_BOOK_NAME = 50
            MAX_AUTHOR = 50
            MAX_PUBLISHER = 40
            MAX_ISBN = 15
            MAX_LATEST_VERSION = 13
            MAX_SHELF = 13
            MAX_BORROWED_BY = 10  # Example, adjust as needed
            # Extract form data
            book_name = request.form['BookName']
            author = request.form['Author']
            publisher = request.form['Publisher']
            isbn = request.form['ISBN']
            latest_version = request.form['LatestVersion']
            shelf = request.form['Shelf']
            borrowed = request.form.get('Borrowed') == 'true'
            borrowed_by = request.form.get('BorrowedBy') or None
            
            # Length checks
            if len(book_name) > MAX_BOOK_NAME:
                message = 'Error: Book name is too long.'
            elif len(author) > MAX_AUTHOR:
                message = 'Error: Author name is too long.'
            elif len(publisher) > MAX_PUBLISHER:
                message = 'Error: Publisher name is too long.'
            elif len(isbn) > MAX_ISBN:
                message = 'Error: ISBN is too long.'
            elif len(latest_version) > MAX_LATEST_VERSION:
                message = 'Error: Latest version is too long.'
            elif len(shelf) > MAX_SHELF:
                message = 'Error: Shelf is too long.'
            elif borrowed_by and len(borrowed_by) > MAX_BORROWED_BY:
                message = 'Error: Borrowed By ID is too long.'

            if message:
                return jsonify({'success': False, 'message': message})
            
            
            if borrowed_by is not None:
                # Query the database to check if the user exists
                cursor.execute("SELECT * FROM users WHERE id = %s", (borrowed_by,))
                user = cursor.fetchone()
                if not user:
                    return jsonify({'success': False, 'message': 'User ID does not exist'})
            
            # Handling the cover image upload
            cover_image = request.files['CoverImage']
            image_update = False
            if cover_image and cover_image.filename != '':
                filename = secure_filename(cover_image.filename)
                file_path = os.path.join('uploads', filename)
                cover_image.save(file_path)
                
                with open(file_path, 'rb') as file:
                    binary_data = file.read()
                image_update = True

            # Construct the update query
            if image_update:
                update_query = """UPDATE Books SET BookName=%s, Author=%s, Publisher=%s, ISBN=%s, LatestVersion=%s, Shelf=%s, Borrowed=%s, BorrowedBy=%s, CoverImage=%s
                                  WHERE EntryNumber=%s"""
                update_values = (book_name, author, publisher, isbn, latest_version, shelf, borrowed, borrowed_by, binary_data, entry_number)
            else:
                update_query = """UPDATE Books SET BookName=%s, Author=%s, Publisher=%s, ISBN=%s, LatestVersion=%s, Shelf=%s, Borrowed=%s, BorrowedBy=%s
                                  WHERE EntryNumber=%s"""
                update_values = (book_name, author, publisher, isbn, latest_version, shelf, borrowed, borrowed_by, entry_number)

            # Execute the update query
            cursor.execute(update_query, update_values)
            mysql.connection.commit()

                
            # Optionally, remove the file after saving its data to the database
            if image_update:
                os.remove(file_path)

            # Return a JSON response upon successful update
            return jsonify({'success': True, 'message': 'Book updated successfully'})
        

        
        # Fetch the book to edit
        cursor.execute("SELECT * FROM Books WHERE EntryNumber = %s", (entry_number,))
        book = cursor.fetchone()

        if book:
            return render_template("EditBooks.html", book=book)
        else:
            return "Book not found", 404
    else:
        return render_template('error-404.html'), 403



# FUNCTION TO DELETE BOOKS
@app.route("/delete_book/<int:entry_number>", methods=['POST'])
def delete_book(entry_number):
    # Check if user is logged in and is a Librarian
    if 'loggedin' in session and session['user_type'] == 'Librarian':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("DELETE FROM Books WHERE EntryNumber = %s", (entry_number,))
            mysql.connection.commit()
            return jsonify({"success": True, "message": "Book deleted successfully"})
        except Exception as e:
            return jsonify({"success": False, "message": str(e)})
    else:
        # Return a message indicating lack of authorization
        return jsonify({"success": False, "message": "Unauthorized access"}), 403


@app.route('/search_books', methods=['GET'])
def search_books():
    # Check if user is logged in and either a Librarian or a Patron
    if 'loggedin' in session and session['user_type'] in ['Librarian', 'Patron']:
        search_query = request.args.get('query', '')  # Get the search query from the URL parameters
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # Prepare the search query for SQL LIKE statement
        search_query = f"%{search_query}%"
        
        # Construct the SQL query to search books
        search_sql = """SELECT Books.*, CONCAT(users.first_name, ' ', users.last_name) AS BorrowerName 
                        FROM Books LEFT JOIN users ON Books.BorrowedBy = users.id 
                        WHERE BookName LIKE %s OR 
                            Author LIKE %s OR 
                            Publisher LIKE %s OR 
                            ISBN LIKE %s"""
        cursor.execute(search_sql, (search_query, search_query, search_query, search_query))
        search_results = cursor.fetchall()

        return render_template('searchBooks.html', search_results=search_results, search_query=request.args.get('query'))
    else:
        # Redirect to the login page or show an unauthorized access message
        return render_template('error-404.html'), 403


@app.route('/validate_credentials', methods=['POST'])
def validate_credentials():
    data = request.get_json()
    email = data.get('email')  # Assuming this is the email
    password = data.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        return jsonify({'success': True, 'message': 'Credentials validated!', 'userId': user['id']})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials!'}), 401

@app.route('/borrow_book', methods=['POST'])
def borrow_book():
    data = request.get_json()
    entry_number = data.get('entryNumber')
    user_id = data.get('userId')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # First, check if the book is already borrowed
        cursor.execute("SELECT Borrowed FROM Books WHERE EntryNumber = %s", (entry_number,))
        book = cursor.fetchone()

        if book and book['Borrowed']:
            # python -m virtualenv envIf the book is already borrowed, return a message indicating so
            return jsonify({'success': False, 'message': 'This book is already borrowed'}), 409

        # If the book is not borrowed, proceed to mark it as borrowed
        cursor.execute("UPDATE Books SET Borrowed = TRUE, BorrowedBy = %s WHERE EntryNumber = %s", (user_id, entry_number))
        mysql.connection.commit()
        return jsonify({'success': True, 'message': 'Book borrowed successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



if __name__ == "__main__":
    app.run()
    os.execv(__file__, sys.argv)

