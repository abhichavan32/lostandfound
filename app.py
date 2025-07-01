import os
import logging
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import uuid
import json

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configuration
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for items
items_storage = []

# Categories for filtering
CATEGORIES = [
    'Electronics', 'Clothing', 'Jewelry', 'Keys', 'Documents', 
    'Bags', 'Books', 'Pets', 'Vehicles', 'Sports Equipment', 'Other'
]

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_item_id():
    return str(uuid.uuid4())[:8]

@app.route('/')
def index():
    # Get recent items for homepage
    recent_lost = [item for item in items_storage if item['type'] == 'lost'][-6:]
    recent_found = [item for item in items_storage if item['type'] == 'found'][-6:]
    
    return render_template('index.html', 
                         recent_lost=recent_lost[::-1], 
                         recent_found=recent_found[::-1])

@app.route('/post/<item_type>')
def post_item_form(item_type):
    if item_type not in ['lost', 'found']:
        flash('Invalid item type', 'error')
        return redirect(url_for('index'))
    
    return render_template('post_item.html', item_type=item_type, categories=CATEGORIES)

@app.route('/post/<item_type>', methods=['POST'])
def post_item(item_type):
    if item_type not in ['lost', 'found']:
        flash('Invalid item type', 'error')
        return redirect(url_for('index'))
    
    try:
        # Validate required fields
        required_fields = ['title', 'description', 'category', 'location', 'contact_name', 'contact_email']
        for field in required_fields:
            if not request.form.get(field):
                flash(f'{field.replace("_", " ").title()} is required', 'error')
                return redirect(url_for('post_item_form', item_type=item_type))
        
        # Handle file upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to prevent filename conflicts
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename
        
        # Create item
        item = {
            'id': generate_item_id(),
            'type': item_type,
            'title': request.form['title'].strip(),
            'description': request.form['description'].strip(),
            'category': request.form['category'],
            'location': request.form['location'].strip(),
            'date_posted': datetime.now().isoformat(),
            'date_lost_found': request.form.get('date_lost_found', ''),
            'contact_name': request.form['contact_name'].strip(),
            'contact_email': request.form['contact_email'].strip(),
            'contact_phone': request.form.get('contact_phone', '').strip(),
            'image': image_filename,
            'status': 'active'
        }
        
        items_storage.append(item)
        
        flash(f'{item_type.title()} item posted successfully!', 'success')
        return redirect(url_for('item_detail', item_id=item['id']))
        
    except Exception as e:
        logging.error(f"Error posting item: {str(e)}")
        flash('An error occurred while posting the item. Please try again.', 'error')
        return redirect(url_for('post_item_form', item_type=item_type))

@app.route('/browse/<item_type>')
def browse_items(item_type):
    if item_type not in ['lost', 'found']:
        flash('Invalid item type', 'error')
        return redirect(url_for('index'))
    
    # Get filter parameters
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    search = request.args.get('search', '')
    
    # Filter items
    filtered_items = []
    for item in items_storage:
        if item['type'] != item_type or item['status'] != 'active':
            continue
        
        # Apply filters
        if category and item['category'] != category:
            continue
        
        if location and location.lower() not in item['location'].lower():
            continue
        
        if search:
            search_lower = search.lower()
            if (search_lower not in item['title'].lower() and 
                search_lower not in item['description'].lower() and
                search_lower not in item['location'].lower()):
                continue
        
        filtered_items.append(item)
    
    # Sort by date posted (newest first)
    filtered_items.sort(key=lambda x: x['date_posted'], reverse=True)
    
    return render_template('browse.html', 
                         items=filtered_items, 
                         item_type=item_type,
                         categories=CATEGORIES,
                         current_category=category,
                         current_location=location,
                         current_search=search)

@app.route('/item/<item_id>')
def item_detail(item_id):
    item = None
    for stored_item in items_storage:
        if stored_item['id'] == item_id:
            item = stored_item
            break
    
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('item_detail.html', item=item)

@app.route('/item/<item_id>/edit')
def edit_item_form(item_id):
    item = None
    for stored_item in items_storage:
        if stored_item['id'] == item_id:
            item = stored_item
            break
    
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('index'))
    
    return render_template('post_item.html', item=item, categories=CATEGORIES, editing=True)

@app.route('/item/<item_id>/edit', methods=['POST'])
def edit_item(item_id):
    item = None
    item_index = None
    for i, stored_item in enumerate(items_storage):
        if stored_item['id'] == item_id:
            item = stored_item
            item_index = i
            break
    
    if not item:
        flash('Item not found', 'error')
        return redirect(url_for('index'))
    
    try:
        # Validate required fields
        required_fields = ['title', 'description', 'category', 'location', 'contact_name', 'contact_email']
        for field in required_fields:
            if not request.form.get(field):
                flash(f'{field.replace("_", " ").title()} is required', 'error')
                return redirect(url_for('edit_item_form', item_id=item_id))
        
        # Handle file upload
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
                filename = timestamp + filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                item['image'] = filename
        
        # Update item
        item.update({
            'title': request.form['title'].strip(),
            'description': request.form['description'].strip(),
            'category': request.form['category'],
            'location': request.form['location'].strip(),
            'date_lost_found': request.form.get('date_lost_found', ''),
            'contact_name': request.form['contact_name'].strip(),
            'contact_email': request.form['contact_email'].strip(),
            'contact_phone': request.form.get('contact_phone', '').strip(),
        })
        
        items_storage[item_index] = item
        
        flash('Item updated successfully!', 'success')
        return redirect(url_for('item_detail', item_id=item_id))
        
    except Exception as e:
        logging.error(f"Error updating item: {str(e)}")
        flash('An error occurred while updating the item. Please try again.', 'error')
        return redirect(url_for('edit_item_form', item_id=item_id))

@app.route('/item/<item_id>/delete', methods=['POST'])
def delete_item(item_id):
    item_index = None
    for i, stored_item in enumerate(items_storage):
        if stored_item['id'] == item_id:
            item_index = i
            break
    
    if item_index is not None:
        items_storage.pop(item_index)
        flash('Item deleted successfully', 'success')
    else:
        flash('Item not found', 'error')
    
    return redirect(url_for('index'))

@app.route('/search')
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('index'))
    
    # Search through all active items
    results = []
    query_lower = query.lower()
    
    for item in items_storage:
        if item['status'] != 'active':
            continue
        
        if (query_lower in item['title'].lower() or 
            query_lower in item['description'].lower() or
            query_lower in item['location'].lower() or
            query_lower in item['category'].lower()):
            results.append(item)
    
    # Sort by date posted (newest first)
    results.sort(key=lambda x: x['date_posted'], reverse=True)
    
    return render_template('browse.html', 
                         items=results, 
                         item_type='search',
                         categories=CATEGORIES,
                         search_query=query)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
