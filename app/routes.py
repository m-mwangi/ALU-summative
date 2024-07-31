from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.database import db
from app.models import User, Conversation, Message
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegistrationForm, EditProfileForm

auth = Blueprint('auth', __name__)
routes_bp = Blueprint('routes', __name__)
main = Blueprint('main', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', title='Login', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User created successfully!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('auth.login'))

@main.route('/', methods=['GET'])
@login_required
def home():
    query = request.args.get('query')
    users = User.query.filter(User.username.ilike(f"%{query}%")).all() if query else []
    conversations = Conversation.query.filter(Conversation.participants.contains(current_user)).all()
    return render_template('home.html', conversations=conversations, users=users)

@main.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('main.home'))
    return render_template('profile.html', user=user)

@main.route('/profile/<username>/edit', methods=['GET', 'POST'])
@login_required
def edit_profile(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User not found!', 'danger')
        return redirect(url_for('main.home'))

    if user != current_user:
        flash('You can only edit your own profile!', 'warning')
        return redirect(url_for('main.profile', username=username))

    form = EditProfileForm()

    if form.validate_on_submit():
        user.bio = form.bio.data
        if form.profile_picture.data:
            filename = secure_filename(form.profile_picture.data.filename)
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            form.profile_picture.data.save(filepath)
            user.profile_picture = filename
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.profile', username=username))

    form.bio.data = user.bio
    form.profile_picture.data = user.profile_picture
    return render_template('edit_profile.html', user=user, form=form)

@main.route('/conversations')
@login_required
def conversations():
    conversations = current_user.conversations
    return render_template('conversations.html', conversations=conversations)

@main.route('/conversation/<int:conversation_id>')
@login_required
def conversation(conversation_id):
    conversation = Conversation.query.get_or_404(conversation_id)
    if current_user not in conversation.participants:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.home'))
    messages = conversation.messages.order_by(Message.timestamp.asc())

    # Mark all messages as read for the current user
    for message in messages:
        if message.recipient == current_user and not message.is_read:
            message.is_read = True
    db.session.commit()

    return render_template('conversation.html', conversation=conversation, messages=messages)

@main.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    recipient_username = data.get('recipient_username')
    message_content = data.get('message')

    if not recipient_username or not message_content:
        return jsonify({'error': 'Recipient username and message content are required'}), 400

    recipient = User.query.filter_by(username=recipient_username).first()
    if not recipient:
        return jsonify({'error': 'Recipient not found'}), 404

    conversation = Conversation.query.filter(Conversation.participants.contains(current_user),
                                             Conversation.participants.contains(recipient)).first()

    if not conversation:
        conversation = Conversation(participants=[current_user, recipient])
        db.session.add(conversation)
        db.session.commit()

    message = Message(sender=current_user, recipient=recipient, content=message_content, conversation=conversation)
    db.session.add(message)
    db.session.commit()

    return jsonify({'message': 'Message sent successfully'}) 
