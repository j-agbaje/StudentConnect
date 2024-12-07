import os
from werkzeug.utils import secure_filename


from flask_mail import Message as MailMessage
from flask_socketio import SocketIO, join_room, leave_room, send
import json
from elasticsearch import Elasticsearch, helpers
from elasticsearch.helpers import bulk
from elasticsearch.exceptions import NotFoundError
from elasticsearch_dsl import Search
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, current_app
from StudentConnect import app,db, bcrypt, socketio, mail
from StudentConnect.models import User, Message
from StudentConnect.forms import RegistrationForm, LoginForm, EditProfileForm
from datetime import datetime, timezone
from flask_login import login_user, current_user, logout_user, login_required






config_path = os.path.join(os.path.dirname(__file__), '../config.json')



# def save_message(room, message, username):
#     new_message = Message(
#         room=room,
#         message=message,
#         username=username,
#         created_at=datetime.now()
#     )
#     db.session.add(new_message)
#     db.session.commit()
def save_picture(form_picture):
    if form_picture == 'default.jpg':
        # Open the default.jpg image, resize it, and save it
        picture_path = os.path.join(current_app.root_path, 'static/images/profile_pics', 'default.jpg')
        output_size = (125, 125)
    

        # Open the image, resize it, and save
        i = Image.open(picture_path)
        i.thumbnail(output_size)
        i.save(picture_path)
        
        return 'default.jpg'
    # Generate a random hexadecimal string to use as part of the filename
    else:
        random_hex = secrets.token_hex(8)
        
        # Get the file extension
        _, f_ext = os.path.splitext(form_picture.filename)
        
        # Generate a filename based on the random string and file extension
        picture_fn = random_hex + f_ext
        
        # Define the path to save the image
        picture_path = os.path.join(app.root_path, 'static/images/profile_pics', picture_fn)
        
        # Open the image file using Pillow
        i = Image.open(form_picture)
        
        # Resize image while maintaining aspect ratio
        output_size = (125, 125)
        i.thumbnail(output_size)
        
        # Save the resized image
        i.save(picture_path)
        
        # Return the filename of the saved image
        return picture_fn
def save_message(room, message_content, sender_id, receiver_id):
    new_message = Message(
        room=room,
        message_content=message_content,
        sender_id=sender_id,
        receiver_id=receiver_id,
        timestamp=datetime.now(timezone.utc)
    )
    db.session.add(new_message)
    db.session.commit() 



try:
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print(f"Config file not found at {config_path}")
except json.JSONDecodeError:
    print("Error decoding JSON file. Please check its format.")


es = Elasticsearch(
    "https://6eb25373254e449fab3f18eac554e1e1.us-central1.gcp.cloud.es.io:443",
    api_key=os.getenv('ELASTICSEARCH_API_KEY'))
    


try:
    if not es.indices.exists(index="user_profiles"):
        es.indices.create(index="user_profiles")
except Exception as e:
    print(f"Error creating index: {e}")









# Route to the homepage
@app.route("/")
def home():
    return render_template("index.html")

# Registration route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()

    # Check if the form is submitted and valid
    if form.validate_on_submit():
        # Save the profile picture and get the filename
        if form.profile_picture.data:
            picture_file = form.profile_picture.data
        else:
            # If no picture is uploaded, use a default picture
            picture_file = 'default.jpg'
        
        # Update the current user's profile picture
        # current_user.profile_picture = picture_file
        
        # Check if the mobile number already exists
        existing_user = User.query.filter_by(mobile_number=form.mobile_number.data).first()
        if existing_user:
            form.mobile_number.errors.append("This mobile number is already registered.")  # Add error to the field
            return render_template("register.html", title='Register', form=form)  # Return form with errors
        
        # Check if the WhatsApp number already exists
        existing_user_whatsapp = User.query.filter_by(whatsapp_number=form.whatsapp_number.data).first()
        if existing_user_whatsapp:
            form.whatsapp_number.errors.append("This WhatsApp number is already registered.")  # Add error to the field
            return render_template("register.html", title='Register', form=form)  # Return form with errors
        
        # Check if the Instagram handle already exists
        existing_user_instagram = User.query.filter_by(instagram_handle=form.instagram_handle.data).first()
        if existing_user_instagram:
            form.instagram_handle.errors.append("This Instagram handle is already registered.")  # Add error to the field
            return render_template("register.html", title='Register', form=form)  # Return form with errors
        
        # Check if the LinkedIn handle already exists
        existing_user_linkedin = User.query.filter_by(linkedin_handle=form.linkedin_handle.data).first()
        if existing_user_linkedin:
            form.linkedin_handle.errors.append("This LinkedIn handle is already registered.")  # Add error to the field
            return render_template("register.html", title='Register', form=form)  # Return form with errors
        
        # Hash the password before storing it in the database
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Create a new user instance
        new_user = User(
            full_name=form.full_name.data,
            username=form.username.data,
            email=form.email.data,
            password=hashed_password,
            school=form.school.data,
            primary_language=form.primary_language.data,
            other_languages=form.other_language.data,
            country=form.country.data,
            course=form.course.data,
            profile_picture=picture_file,  # Save the profile picture filename
            mobile_number=form.mobile_number.data,
            whatsapp_number=form.whatsapp_number.data,
            linkedin_handle=form.linkedin_handle.data,
            instagram_handle=form.instagram_handle.data,
            interests=form.interests.data,
            bio=form.bio.data
        )

        db.session.add(new_user)
        try:
    # Commit changes to the database
            db.session.commit()

    # Update Elasticsearch index
            user_profile = {
                "_index": "user_profiles",  # Specify the index name
                "_id": new_user.id,  # Use the user ID as the document ID
                "_source": {
                    "full_name": new_user.full_name,
                    "username": new_user.username,
                    "email": new_user.email,
                    "school": new_user.school,
                    "primary_language": new_user.primary_language,
                    "other_languages": new_user.other_languages,
                    "country": new_user.country,
                    "course": new_user.course,
                    "bio": new_user.bio,
                    "profile_picture": new_user.profile_picture
                },
            }

    # Update the document in Elasticsearch
            es.index(index="user_profiles", id=new_user.id, body=user_profile['_source'])

            flash('Your account has been created!', 'success')
            login_user(new_user)
            return redirect(url_for('home'))  # Redirect to the profile page

        except Exception as e:
            db.session.rollback()  # Roll back the changes in case of any error
            flash(f'An error occurred while updating your profile: {str(e)}', 'danger')
    return render_template("register.html", title='Register', form=form)







# Profile route
@app.route("/profile")
@login_required
def profile():
    user = current_user
    image_file = url_for("static", filename=f'profile_pics/{current_user.profile_picture}')
    return render_template("profile.html", user=user, image_file=image_file)

# Layout route
@app.route("/layout")
def layout():
    return render_template("layout.html")

# Login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Login Successful! Welcome {user.username}', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful, Invalid email or password', 'danger')
            
    return render_template("login.html", title='Login', form=form)



@app.route("/logout")
def logout():
    logout_user()
    flash(f'User logged out', 'primary')
    return redirect(url_for('home'))

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/about")
def about():
    return render_template('about.html')





@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()

    # Prefill the form with the current user's data on GET requests
    if request.method == 'GET':
        form.full_name.data = current_user.full_name
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.school.data = current_user.school
        form.primary_language.data = current_user.primary_language
        form.other_language.data = current_user.other_languages
        form.country.data = current_user.country
        form.course.data = current_user.course
        form.mobile_number.data = current_user.mobile_number
        form.whatsapp_number.data = current_user.whatsapp_number
        form.instagram_handle.data = current_user.instagram_handle
        form.linkedin_handle.data = current_user.linkedin_handle
        form.interests.data = current_user.interests
        form.bio.data = current_user.bio

    # Handle form submission and update all fields
    if form.validate_on_submit():
        if form.profile_picture.data:
            picture_file = save_picture(form.profile_picture.data)
            current_user.profile_picture = picture_file

        current_user.full_name = form.full_name.data
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.school = form.school.data
        current_user.primary_language = form.primary_language.data
        current_user.other_language = form.other_language.data
        current_user.country = form.country.data
        current_user.course = form.course.data
        current_user.mobile_number = form.mobile_number.data
        current_user.whatsapp_number = form.whatsapp_number.data
        current_user.instagram_handle = form.instagram_handle.data
        current_user.linkedin_handle = form.linkedin_handle.data
        current_user.interests = form.interests.data
        current_user.bio = form.bio.data

        try:
            # Commit changes to the database
            db.session.commit()

            # Update Elasticsearch index
            user_profile = {
                "_index": "user_profiles",  # Specify the index name
                "_id": current_user.id,  # Use the user ID as the document ID
                "_source": {
                    "full_name": current_user.full_name,
                    "username": current_user.username,
                    "email": current_user.email,
                    "school": current_user.school,
                    "primary_language": current_user.primary_language,
                    "other_languages": current_user.other_languages,
                    "country": current_user.country,
                    "course": current_user.course,
                    "bio": current_user.bio,
                    "profile_picture": current_user.profile_picture
                },
            }

            # Update the document in Elasticsearch
            es.index(index="user_profiles", id=current_user.id, body=user_profile['_source'])

            flash("Your profile has been updated!", "success")
            return redirect(url_for('profile'))  # Redirect to the profile page

        except Exception as e:
            db.session.rollback()  # Roll back the changes in case of any error
            flash(f'An error occurred while updating your profile: {str(e)}', 'danger')

    # Render the form with existing data
    image_file = url_for('static', filename='images/profile_pics/' + current_user.profile_picture)
    return render_template('edit_profile.html', title="Edit Profile", image_file=image_file, form=form)



# @app.route('/search')
# def search():
#     data = ""
#     es_error = ""
   
#     data = es.search(index="user_profiles", body={"query": {"match_all": {}}})

#     profiles_list = []
#     if data:
#         for i in data['hits']['hits']:
#             profiles_list.append(i['_source'])
#     return render_template("search.html", data=profiles_list, es_error=es_error)



@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
    users = User.query.all()  # Fetch all users from the database
    query = ""  # Default value for the search query
    
    if request.method == 'POST':
        query = request.form['search']  # Assign query value for POST requests

    # Perform search only if a query exists
    if query:
        data = es.search(index="user_profiles", body={
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["full_name", "username", "school", "primary_language", "course"]
                }
            }
        })
        profiles_list = []
        for i in data['hits']['hits']:
            profile = i['_source']
            # Check if 'profile_picture' exists or is empty
            if 'profile_picture' not in profile or not profile['profile_picture']:
                profile['profile_picture'] = './StudentConnect/static/images/profile_pics/default.jpg'  # Set default profile picture
            profiles_list.append(profile)
            es_error = None
    else:
        profiles_list = []  # No query, return an empty list or handle as needed
        es_error = "Please enter a search term."

    return render_template("test_search.html", data=profiles_list, users=users, query=query, es_error=es_error)



def delete_old_users_from_es():
    # Step 1: Query all users from the database
    users = User.query.all()  # Get active users from the database
    user_ids_in_db = set(user.id for user in users)  # Get a set of active user IDs

    # Step 2: Query Elasticsearch to get all user IDs
    try:
        es_users = es.search(
            index="user_profiles",
            body={
                "query": {
                    "match_all": {}  # Match all documents in the "user_profiles" index
                },
                "_source": ["_id"],  # Only retrieve the document ID (_id)
                "size": 10000  # Limit to a reasonable number, adjust as necessary
            }
        )
    except Exception as e:
        print(f"Error querying Elasticsearch: {e}")
        return

    es_user_ids = set(hit['_id'] for hit in es_users['hits']['hits'])  # Get user IDs from Elasticsearch

    # Step 3: Find user IDs in Elasticsearch that are not in the database
    deleted_user_ids = es_user_ids - user_ids_in_db  # Get IDs of users that no longer exist in the database

    # Step 4: Delete those users from Elasticsearch
    for user_id in deleted_user_ids:
        try:
            es.delete(index="user_profiles", id=user_id)  # Delete the document from Elasticsearch
            print(f"Deleted user with ID {user_id} from Elasticsearch.")
        except NotFoundError:
            print(f"User with ID {user_id} not found in Elasticsearch.")
        except Exception as e:
            print(f"Error deleting user with ID {user_id} from Elasticsearch: {e}")

    return f"Deleted {len(deleted_user_ids)} user(s) from Elasticsearch."


    
@app.route("/index_current_users")
def index_current_users():
    delete_old_users_from_es()
    # Query all users from the database
    users = User.query.all()
    profiles_list = []

    # Convert each user to the desired format
    for user in users:
        user_profile = {
            "_index": "user_profiles",  # Specify the index name
            "_id": user.id,  # Use the user ID as the document ID
            "_source": {
                "full_name": user.full_name,
                "username": user.username,
                "email": user.email,
                "school": user.school,
                "primary_language": user.primary_language,
                "other_languages": user.other_languages,
                "country": user.country,
                "course": user.course,
                "bio": user.bio,
            },
        }
        profiles_list.append(user_profile)

    # Use the bulk helper to index all profiles
    try:
        data = bulk(
            es,
            profiles_list,
        )
        success_count = data[0]  # Number of successful operations
    except Exception as e:
        success_count = f"Error during bulk indexing: {str(e)}"

    return render_template("index_current_users.html", data=success_count)



@app.route("/user_profile/<username>")
def user_profile(username):
    # Fetch the user by their username
    user = User.query.filter_by(username=username).first()
    
    # Check if user exists
    if user:
        # You can add the user's profile data to the context here
        return render_template("display_profile.html", user=user)
    else:
        # If no user is found, show an error or redirect to a different page
        return redirect(url_for('search'))  # Redirect back to search page or show an error message
    

@app.route("/message_request/<int:recipient_id>", methods=["POST"])
def message_request(recipient_id):
    if not current_user.is_authenticated:
        flash("You need to be logged in to send a message request.", "danger")
        return redirect(url_for('login'))

    recipient = User.query.get_or_404(recipient_id)
    room = f"chat_{min(current_user.id, recipient.id)}_{max(current_user.id, recipient.id)}"  # Unique room name
    chat_url = f"https://b75c-31-13-189-154.ngrok-free.app/chat/{room}"

    # Send email to recipient
    msg = MailMessage(
        subject=f"Message Request from {current_user.full_name}",
        recipients=[recipient.email],
        sender='jeremiahagbaje99@gmail.com',
        body=f"""
        Hello {recipient.full_name},

        {current_user.username} has sent you a message request. 
        Click the link below to join the chat room:

        {chat_url}

        Best regards,
        StudentConnect Team
        """
    )
    mail.send(msg)

    flash("Message request sent successfully!", "success")
    return redirect(url_for('chat', room=room))

# Route for the chat page where users will land
@app.route("/chat/<string:room>")
@login_required
def chat(room):
    return render_template("chat.html", room=room, username=current_user.username)

# Socket event: user sending a message
@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info(f"{data['username']} has sent a message to room {data['room']}: {data['message']}")
    data['created_at'] = datetime.now().strftime("%d %b, %H:%M")
    # Save the message in the database (ensure room is saved with the message)
    message = Message(sender_id=current_user.id, receiver_id=data['receiver_id'], room=data['room'], message_content=data['message'])
    db.session.add(message)
    db.session.commit()

    # Emit the message to all users in the room
    socketio.emit('receive_message', data, room=data['room'])

# Socket event: user joining a room
@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info(f"{data['username']} has joined the room {data['room']}")
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])

# Socket event: user leaving a room
@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info(f"{data['username']} has left the room {data['room']}")
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])