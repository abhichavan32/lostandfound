# 🚀 Deployment Guide for Lost & Found Application

This guide will help you deploy your Lost & Found application to various hosting platforms.

## 📋 Pre-Deployment Checklist

- [ ] Update environment variables
- [ ] Configure database for production
- [ ] Set up file storage
- [ ] Configure domain and SSL
- [ ] Set up monitoring and logging

## 🌐 Deployment Options

### Option 1: Render (Recommended for Beginners)

#### Step 1: Prepare Your Repository
1. Push your code to GitHub/GitLab
2. Ensure you have the following files:
   - `requirements.txt`
   - `wsgi.py`
   - `config.py`
   - `.env` (with production values)

#### Step 2: Deploy on Render
1. Go to [render.com](https://render.com) and sign up
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `lost-and-found-app`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app`
   - **Plan**: Free (or paid for production)

#### Step 3: Environment Variables
Add these environment variables in Render:
```
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=your-production-database-url
UPLOAD_FOLDER=/opt/render/project/src/static/uploads
```

#### Step 4: Database Setup
1. Create a new MySQL database on Render or use external service
2. Update `DATABASE_URL` in environment variables
3. Run database migrations

### Option 2: Railway

#### Step 1: Deploy on Railway
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" and select "Deploy from GitHub repo"
3. Select your repository
4. Railway will auto-detect Python and deploy

#### Step 2: Environment Variables
Add the same environment variables as in Render

### Option 3: Heroku

#### Step 1: Install Heroku CLI
```bash
# Windows
winget install --id=Heroku.HerokuCLI

# macOS
brew tap heroku/brew && brew install heroku

# Linux
curl https://cli-assets.heroku.com/install.sh | sh
```

#### Step 2: Deploy
```bash
# Login to Heroku
heroku login

# Create app
heroku create your-app-name

# Add buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=your-database-url

# Deploy
git push heroku main
```

### Option 4: AWS (Advanced)

#### Step 1: Set up AWS Account
1. Create AWS account
2. Install AWS CLI
3. Configure credentials

#### Step 2: Deploy with Elastic Beanstalk
```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init

# Create environment
eb create production

# Deploy
eb deploy
```

## 🗄️ Database Setup

### MySQL on Cloud
1. **PlanetScale** (Free tier available)
2. **AWS RDS** (Pay-as-you-use)
3. **Google Cloud SQL** (Free tier available)
4. **Azure Database** (Free tier available)

### Database Migration
```bash
# Create production database
mysql -u username -p -h hostname
CREATE DATABASE lost_and_found_prod;

# Update environment variables
DATABASE_URL=mysql://username:password@hostname:3306/lost_and_found_prod

# Run migrations (if you have them)
python init_db.py
```

## 📁 File Storage

### Local Storage (Development)
- Files stored in `static/uploads/`
- Good for testing, not for production

### Cloud Storage (Production)
1. **AWS S3** (Recommended)
2. **Google Cloud Storage**
3. **Azure Blob Storage**

### S3 Setup Example
```python
# Add to requirements.txt
boto3>=1.26.0

# Update config.py
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_ACCESS_KEY = os.environ.get('S3_ACCESS_KEY')
S3_SECRET_KEY = os.environ.get('S3_SECRET_KEY')
S3_REGION = os.environ.get('S3_REGION', 'us-east-1')
```

## 🔒 Security Configuration

### Environment Variables
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_hex(32))"

# Set in production
SECRET_KEY=your-generated-secret-key
FLASK_ENV=production
```

### Security Headers
```python
# Add to your app
from flask_talisman import Talisman

Talisman(app, 
    content_security_policy={
        'default-src': "'self'",
        'img-src': "'self' data: https:",
        'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
        'style-src': "'self' 'unsafe-inline' https:",
    }
)
```

## 📊 Monitoring & Logging

### Application Monitoring
1. **Sentry** (Error tracking)
2. **LogRocket** (User session replay)
3. **Google Analytics** (Traffic analysis)

### Logging Setup
```python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/lost_andfound.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Lost and Found startup')
```

## 🚀 Performance Optimization

### Gunicorn Configuration
```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 2
```

### Database Optimization
```python
# Add to config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20,
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Example
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Render
      uses: johnbeynon/render-deploy-action@v1.0.0
      with:
        service-id: ${{ secrets.RENDER_SERVICE_ID }}
        api-key: ${{ secrets.RENDER_API_KEY }}
```

## 🧪 Testing Before Deployment

### Local Testing
```bash
# Test production config
export FLASK_ENV=production
export DATABASE_URL=your-test-db-url
python -m pytest

# Test with gunicorn
gunicorn wsgi:app --bind 0.0.0.0:8000
```

### Health Check Endpoint
```python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected' if db.engine.execute('SELECT 1') else 'disconnected'
    })
```

## 📱 Domain & SSL Setup

### Custom Domain
1. Purchase domain from registrar (Namecheap, GoDaddy, etc.)
2. Point DNS to your hosting provider
3. Configure SSL certificate

### SSL Certificate
- **Let's Encrypt** (Free)
- **Cloudflare** (Free SSL)
- **Hosting provider SSL** (Usually included)

## 🆘 Troubleshooting

### Common Issues
1. **Database Connection**: Check `DATABASE_URL` format
2. **File Uploads**: Verify `UPLOAD_FOLDER` permissions
3. **Static Files**: Ensure proper static file serving
4. **Environment Variables**: Verify all required vars are set

### Debug Commands
```bash
# Check environment
heroku config  # Heroku
render env     # Render

# View logs
heroku logs --tail  # Heroku
render logs         # Render

# Run shell
heroku run python  # Heroku
render shell       # Render
```

## 📚 Additional Resources

- [Flask Deployment Documentation](https://flask.palletsprojects.com/en/2.3.x/deploying/)
- [Gunicorn Configuration](https://docs.gunicorn.org/en/stable/configure.html)
- [Render Documentation](https://render.com/docs)
- [Railway Documentation](https://docs.railway.app/)
- [Heroku Documentation](https://devcenter.heroku.com/)

## 🎯 Next Steps

After deployment:
1. Set up monitoring and alerts
2. Configure backup strategies
3. Implement CI/CD pipeline
4. Set up staging environment
5. Plan for scaling

---

**Need Help?** Check the troubleshooting section or create an issue in your repository.
