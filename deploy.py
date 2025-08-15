#!/usr/bin/env python3
"""
Deployment script for Lost & Found application
This script helps automate the deployment process
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path

def print_header(title):
    """Print a formatted header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return None

def check_requirements():
    """Check if required tools are installed"""
    print_header("Checking Requirements")
    
    tools = {
        'git': 'Git version control',
        'python': 'Python interpreter',
        'pip': 'Python package manager'
    }
    
    missing_tools = []
    
    for tool, description in tools.items():
        try:
            subprocess.run([tool, '--version'], capture_output=True, check=True)
            print(f"✅ {description} ({tool}) - Found")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"❌ {description} ({tool}) - Missing")
            missing_tools.append(tool)
    
    if missing_tools:
        print(f"\n⚠️  Missing tools: {', '.join(missing_tools)}")
        print("Please install the missing tools before continuing.")
        return False
    
    return True

def generate_secret_key():
    """Generate a secure secret key"""
    return secrets.token_hex(32)

def create_env_file():
    """Create .env file with production values"""
    print_header("Creating Environment File")
    
    env_content = f"""# Production Environment Variables
FLASK_ENV=production
SECRET_KEY={generate_secret_key()}
DATABASE_URL=mysql://username:password@host:port/database_name
UPLOAD_FOLDER=/opt/render/project/src/static/uploads

# Add your actual database credentials here
# DATABASE_URL=mysql://your_user:your_password@your_host:3306/your_database

# Optional: Email configuration
# MAIL_SERVER=smtp.gmail.com
# MAIL_PORT=587
# MAIL_USE_TLS=True
# MAIL_USERNAME=your-email@gmail.com
# MAIL_PASSWORD=your-app-password
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file")
    print("⚠️  Remember to update DATABASE_URL with your actual database credentials")

def check_files():
    """Check if all required files exist"""
    print_header("Checking Required Files")
    
    required_files = [
        'requirements.txt',
        'wsgi.py',
        'config.py',
        'app.py',
        'models.py'
    ]
    
    missing_files = []
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file} - Found")
        else:
            print(f"❌ {file} - Missing")
            missing_files.append(file)
    
    if missing_files:
        print(f"\n⚠️  Missing files: {', '.join(missing_files)}")
        return False
    
    return True

def test_local_deployment():
    """Test the application locally with production settings"""
    print_header("Testing Local Deployment")
    
    # Test with gunicorn if available
    try:
        subprocess.run(['gunicorn', '--version'], capture_output=True, check=True)
        print("✅ Gunicorn found - testing production server...")
        
        # Start gunicorn in background
        process = subprocess.Popen([
            'gunicorn', 'wsgi:app', 
            '--bind', '0.0.0.0:8000',
            '--workers', '1',
            '--timeout', '30'
        ])
        
        print("✅ Gunicorn started on http://localhost:8000")
        print("⚠️  Press Ctrl+C to stop the server")
        
        try:
            process.wait()
        except KeyboardInterrupt:
            process.terminate()
            print("\n✅ Server stopped")
            
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Gunicorn not found - testing with Flask development server...")
        print("⚠️  This is not recommended for production")
        
        # Test with Flask
        result = run_command(
            'python -c "from app import app; print(\"✅ App imports successfully\")"',
            "Testing app import"
        )
        
        if result:
            print("✅ Application can be imported successfully")

def show_deployment_instructions():
    """Show deployment instructions for different platforms"""
    print_header("Deployment Instructions")
    
    print("\n🌐 Choose your deployment platform:")
    
    print("\n1️⃣  RENDER (Recommended for beginners)")
    print("   - Free tier available")
    print("   - Easy setup")
    print("   - Automatic deployments")
    print("   📖 Guide: https://render.com/docs")
    
    print("\n2️⃣  RAILWAY")
    print("   - Free tier available")
    print("   - Simple deployment")
    print("   - Good performance")
    print("   📖 Guide: https://docs.railway.app/")
    
    print("\n3️⃣  HEROKU")
    print("   - Excellent developer experience")
    print("   - Great add-ons")
    print("   - No free tier (paid only)")
    print("   📖 Guide: https://devcenter.heroku.com/")
    
    print("\n4️⃣  AWS (Advanced)")
    print("   - Highly scalable")
    print("   - Pay-as-you-use")
    print("   - Complex setup")
    print("   📖 Guide: https://aws.amazon.com/")
    
    print("\n📋 Next Steps:")
    print("1. Choose a platform from above")
    print("2. Follow the platform-specific guide")
    print("3. Set up your database")
    print("4. Configure environment variables")
    print("5. Deploy your application")
    
    print("\n📚 Full deployment guide available in DEPLOYMENT.md")

def main():
    """Main deployment script"""
    print_header("Lost & Found Application Deployment")
    
    print("This script will help you prepare your application for deployment.")
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check required files
    if not check_files():
        print("\n❌ Please ensure all required files exist before continuing.")
        sys.exit(1)
    
    # Create environment file
    create_env_file()
    
    # Test local deployment
    test_local_deployment()
    
    # Show deployment instructions
    show_deployment_instructions()
    
    print_header("Deployment Preparation Complete")
    print("✅ Your application is ready for deployment!")
    print("📖 Check DEPLOYMENT.md for detailed instructions")
    print("🔧 Update .env file with your actual credentials")

if __name__ == "__main__":
    main()
