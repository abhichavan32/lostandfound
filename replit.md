# Lost & Found Web Application

## Overview

This is a Flask-based web application for managing lost and found items with full user authentication and notification system. Users can register accounts, log in, and manage their personal lost and found items. The system automatically sends notifications to all users when new lost items are posted, helping to increase the chances of reuniting people with their belongings. The application uses PostgreSQL database for persistent storage and includes a comprehensive dashboard for users to manage their items and notifications.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: Flask-Login with secure password hashing
- **File Handling**: Local file system for image uploads
- **Session Management**: Flask sessions with secret key configuration
- **Notifications**: Automatic notification system for lost items
- **Logging**: Built-in Python logging for debugging

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.4.0
- **JavaScript**: Vanilla JavaScript for client-side interactions
- **Responsive Design**: Bootstrap responsive grid system

### Key Technologies
- Python 3.x
- Flask web framework
- Bootstrap 5 (dark theme)
- Font Awesome icons
- HTML5/CSS3/JavaScript

## Key Components

### Core Application Files
- **app.py**: Main Flask application with routes and business logic
- **main.py**: Application entry point for development server
- **models.py**: Placeholder for future database models (currently contains SQLAlchemy examples)

### Frontend Components
- **templates/base.html**: Base template with navigation and common elements
- **templates/index.html**: Homepage with hero section and recent items
- **templates/browse.html**: Item listing page with filtering capabilities
- **templates/item_detail.html**: Individual item detail view
- **templates/post_item.html**: Form for creating/editing items

### Static Assets
- **static/css/style.css**: Custom CSS for enhanced styling
- **static/js/main.js**: Client-side JavaScript for interactivity
- **static/uploads/**: Directory for uploaded item images

### Core Features
1. **User Authentication**: Complete registration, login, and profile management system
2. **Item Management**: Post, edit, and view lost/found items with owner tracking
3. **Notification System**: Automatic notifications when lost items are posted
4. **User Dashboard**: Personal dashboard showing user's items and notifications
5. **Image Upload**: Support for PNG, JPG, JPEG, GIF, WebP files (16MB limit)
6. **Categorization**: 11 predefined categories for item classification
7. **Search & Filter**: Browse items by type, category, and search terms
8. **Contact System**: Integrated contact through user profiles

## Data Flow

### Item Creation Flow
1. User navigates to post item form
2. Form validates input data and uploaded images
3. System generates unique 8-character item ID
4. Item data stored in in-memory storage
5. Images saved to local file system
6. User redirected to item detail page

### Item Browsing Flow
1. User accesses browse page or searches
2. System filters items based on criteria
3. Results displayed with pagination support
4. Users can view detailed item information
5. Contact information provided for coordination

### File Upload Process
1. File validation (type, size, security)
2. Secure filename generation
3. File saved to uploads directory
4. Filename stored with item record

## External Dependencies

### CDN Resources
- Bootstrap 5 CSS (Replit dark theme variant)
- Font Awesome 6.4.0 icons
- Bootstrap 5 JavaScript bundle

### Python Packages
- Flask (web framework)
- Werkzeug (utilities, file handling)
- Standard library modules (os, logging, datetime, uuid, json)

### Environment Variables
- `SESSION_SECRET`: Flask session secret key (defaults to development key)

## Deployment Strategy

### Current Setup
- Development server configuration
- Local file storage for uploads
- In-memory data storage
- Debug mode enabled for development

### Production Considerations
- **Database Integration**: Ready for SQLAlchemy implementation (models.py contains schema examples)
- **File Storage**: Can be extended to cloud storage (S3, etc.)
- **Session Management**: Production secret key required
- **Security**: CSRF protection, input validation implemented
- **Scalability**: Architecture supports horizontal scaling with database backend

### Deployment Requirements
- Python 3.x runtime
- Flask and dependencies
- File system write permissions for uploads
- Environment variable configuration

## Changelog
- July 01, 2025. Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.