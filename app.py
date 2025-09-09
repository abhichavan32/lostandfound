import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv
import uuid

# Import config + models
from config import get_config
from models import db, User, Item, Notification

# --- Load environment variables ---
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class Base(DeclarativeBase):
    pass


# Create Flask app
app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_ENV', 'development')
app.config.from_object(get_config())

# --- Database URL Fix for Supabase ---
db_url = os.getenv("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

if db_url and "sslmode" not in db_url:
    db_url += "?sslmode=require"

if not db_url:
    raise ValueError("❌ DATABASE_URL is not set. Please configure it in Render/Supabase.")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Init DB
db.init_app(app)

# Ensure tables exist
with app.app_context():
    db.create_all()

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Configuration for uploads
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Categories for filtering
CATEGORIES = [
    'Electronics', 'Clothing', 'Jewelry', 'Keys', 'Documents',
    'Bags', 'Books', 'Pets', 'Vehicles', 'Sports Equipment', 'Other'
]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_item_id():
    return str(uuid.uuid4())[:8]


def create_notification_for_lost_item(item):
    """Create notifications for all users when a lost item is posted"""
    try:
        users = User.query.filter(User.id != item.user_id).all()
        for user in users:
            notification = Notification(
                title=f"New Lost Item Posted: {item.title}",
                message=f"A new lost item '{item.title}' was posted in {item.location}.",
                type='lost_item',
                user_id=user.id,
                item_id=item.id
            )
            db.session.add(notification)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error creating notifications: {str(e)}")


# ===================
# AUTH ROUTES
# ===================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        phone = request.form.get('phone')

        if not all([username, email, password, first_name, last_name]):
            flash('Please fill in all required fields.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            phone=phone
        )

        try:
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            logging.error(f"Registration error: {str(e)}")
            flash('Registration failed. Please try again.', 'error')

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('auth/login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))


# ===================
# DASHBOARD & NOTIFICATIONS
# ===================

@app.route('/dashboard')
@login_required
def dashboard():
    user_items = Item.query.filter_by(user_id=current_user.id).order_by(Item.date_posted.desc()).all()
    lost_items = Item.query.filter_by(user_id=current_user.id, type='lost').all()
    found_items = Item.query.filter_by(user_id=current_user.id, type='found').all()
    unread_notifications = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    recent_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()).limit(5).all()

    return render_template('dashboard.html',
                           user_items=user_items,
                           lost_items=lost_items,
                           found_items=found_items,
                           unread_notifications=unread_notifications,
                           recent_notifications=recent_notifications)


@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(
        Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)


@app.route('/notifications/<int:notification_id>/mark_read')
@login_required
def mark_notification_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    return redirect(url_for('notifications'))


# ===================
# MAIN ROUTES
# ===================

@app.route('/')
def index():
    recent_lost = Item.query.filter_by(type='lost', status='active').order_by(Item.date_posted.desc()).limit(6).all()
    recent_found = Item.query.filter_by(type='found', status='active').order_by(Item.date_posted.desc()).limit(6).all()
    return render_template('index.html', recent_lost=recent_lost, recent_found=recent_found)


@app.route('/post/<item_type>')
@login_required
def post_item_form(item_type):
    if item_type not in ['lost', 'found']:
        flash('Invalid item type', 'error')
        return redirect(url_for('index'))
    return render_template('post_item.html', item_type=item_type, categories=CATEGORIES)


@app.route('/post/<item_type>', methods=['POST'])
@login_required
def post_item(item_type):
    if item_type not in ['lost', 'found']:
        flash('Invalid item type', 'error')
        return redirect(url_for('index'))

    try:
        required_fields = ['title', 'description', 'category', 'location']
        for field in required_fields:
            if not request.form.get(field):
                flash(f'{field.replace("_", " ").title()} is required', 'error')
                return redirect(url_for('post_item_form', item_type=item_type))

        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        item = Item(
            id=generate_item_id(),
            type=item_type,
            title=request.form['title'].strip(),
            description=request.form['description'].strip(),
            category=request.form['category'],
            location=request.form['location'].strip(),
            date_lost_found=request.form.get('date_lost_found', ''),
            image=image_filename,
            user_id=current_user.id
        )

        db.session.add(item)
        db.session.commit()

        if item_type == 'lost':
            create_notification_for_lost_item(item)

        flash(f'{item_type.title()} item posted successfully!', 'success')
        return redirect(url_for('item_detail', item_id=item.id))

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error posting item: {str(e)}")
        flash('An error occurred while posting the item. Please try again.', 'error')
        return redirect(url_for('post_item_form', item_type=item_type))


@app.route('/browse/<item_type>')
def browse_items(item_type):
    if item_type not in ['lost', 'found']:
        flash('Invalid item type', 'error')
        return redirect(url_for('index'))

    category = request.args.get('category', '')
    location = request.args.get('location', '')
    search = request.args.get('search', '')

    query = Item.query.filter_by(type=item_type, status='active')

    if category:
        query = query.filter(Item.category == category)
    if location:
        query = query.filter(Item.location.ilike(f'%{location}%'))
    if search:
        query = query.filter(
            db.or_(
                Item.title.ilike(f'%{search}%'),
                Item.description.ilike(f'%{search}%'),
                Item.location.ilike(f'%{search}%')
            )
        )

    items = query.order_by(Item.date_posted.desc()).all()

    return render_template('browse.html',
                           items=items,
                           item_type=item_type,
                           categories=CATEGORIES,
                           current_category=category,
                           current_location=location,
                           current_search=search)


@app.route('/item/<item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)


@app.route('/item/<item_id>/edit')
@login_required
def edit_item_form(item_id):
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    return render_template('post_item.html', item=item, categories=CATEGORIES, editing=True)


@app.route('/item/<item_id>/edit', methods=['POST'])
@login_required
def edit_item(item_id):
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    try:
        required_fields = ['title', 'description', 'category', 'location']
        for field in required_fields:
            if not request.form.get(field):
                flash(f'{field.replace("_", " ").title()} is required', 'error')
                return redirect(url_for('edit_item_form', item_id=item_id))

        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item.image = filename

        item.title = request.form['title'].strip()
        item.description = request.form['description'].strip()
        item.category = request.form['category']
        item.location = request.form['location'].strip()
        item.date_lost_found = request.form.get('date_lost_found', '')

        db.session.commit()

        flash('Item updated successfully!', 'success')
        return redirect(url_for('item_detail', item_id=item_id))

    except Exception as e:
        db.session.rollback()
        logging.error(f"Error updating item: {str(e)}")
        flash('An error occurred while updating the item. Please try again.', 'error')
        return redirect(url_for('edit_item_form', item_id=item_id))


@app.route('/item/<item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    item = Item.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    try:
        db.session.delete(item)
        db.session.commit()
        flash('Item deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        logging.error(f"Error deleting item: {str(e)}")
        flash('Error deleting item', 'error')

    return redirect(url_for('dashboard'))


@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))

    items = Item.query.filter(
        Item.status == 'active',
        db.or_(
            Item.title.ilike(f'%{query}%'),
            Item.description.ilike(f'%{query}%'),
            Item.location.ilike(f'%{query}%'),
            Item.category.ilike(f'%{query}%')
        )
    ).order_by(Item.date_posted.desc()).all()

    return render_template('browse.html',
                           items=items,
                           item_type='search',
                           categories=CATEGORIES,
                           search_query=query)


# ===================
# ENTRYPOINT
# ===================

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
