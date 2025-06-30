# 🚀 VerifAI Deployment Guide (100% FREE)

This guide will help you deploy your VerifAI application with user authentication and email functionality using completely free services.

## 📋 Prerequisites

- GitHub account
- Domain from Namecheap (verifai.tech)
- Gmail account for email functionality
- Render account (free) OR Fly.io account (free)

## 🎯 Deployment Strategy

- **Frontend**: GitHub Pages or Vercel (already deployed)
- **Backend**: Render (free) OR Fly.io (free)
- **Database**: Render PostgreSQL (free) OR Fly.io PostgreSQL (free)
- **Email**: Gmail SMTP (free)

## 🔧 Step 1: Prepare Backend for Deployment

### 1.1 Update Environment Variables

Create a `.env` file in `verifai-backend/verifai/`:

```bash
# Django Settings
SECRET_KEY=your-super-secret-key-here
DEBUG=False
ALLOWED_HOSTS=verifai.tech,www.verifai.tech,your-backend-url.onrender.com

# Database (will be set by Render/Fly.io)
DATABASE_URL=postgresql://...

# Email Settings
EMAIL_HOST_USER=info.verifai@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

### 1.2 Generate a New Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🚀 Step 2: Deploy Backend (Choose One Option)

### **Option A: Render (Recommended)**

#### 2.1 Connect to Render

1. Go to [Render.com](https://render.com)
2. Sign up with GitHub (free)
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Set the root directory to `verifai-backend/verifai/`

#### 2.2 Configure Environment Variables

In Render dashboard, add these environment variables:

```bash
SECRET_KEY=your-generated-secret-key
DEBUG=False
ALLOWED_HOSTS=verifai.tech,www.verifai.tech,your-app-name.onrender.com
EMAIL_HOST_USER=info.verifai@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

#### 2.3 Add PostgreSQL Database

1. In Render dashboard, click "New" → "PostgreSQL"
2. Choose the free plan
3. Render will automatically set the `DATABASE_URL` environment variable
4. Link the database to your web service

#### 2.4 Deploy

1. Render will automatically detect your Django app
2. It will run migrations and start the server
3. Note your deployment URL (e.g., `https://your-app-name.onrender.com`)

### **Option B: Fly.io (Alternative)**

#### 2.1 Install Fly CLI

```bash
# macOS
brew install flyctl

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"

# Linux
curl -L https://fly.io/install.sh | sh
```

#### 2.2 Deploy to Fly.io

```bash
cd verifai-backend/verifai/
fly auth signup
fly launch
```

#### 2.3 Add Database

```bash
fly postgres create
fly postgres attach <your-db-name>
```

#### 2.4 Set Environment Variables

```bash
fly secrets set SECRET_KEY="your-secret-key"
fly secrets set EMAIL_HOST_PASSWORD="your-gmail-app-password"
```

## 🌐 Step 3: Update Frontend Configuration

### 3.1 Update API Base URL

In your frontend repository, update `verifai-frontend/src/config.js`:

```javascript
let API_BASE_URL = "";

if (process.env.REACT_APP_API_BASE_URL) {
  API_BASE_URL = process.env.REACT_APP_API_BASE_URL;
} else if (window.location.hostname === "localhost") {
  API_BASE_URL = "http://localhost:8000";
} else {
  // Update this with your backend URL
  API_BASE_URL = "https://your-app-name.onrender.com"; // or .fly.dev
}

export default API_BASE_URL;
```

### 3.2 Update CORS Settings

Your backend `settings.py` already has the correct CORS settings for verifai.tech.

### 3.3 Redeploy Frontend

1. Commit and push your changes
2. Your frontend will automatically redeploy

## 🔗 Step 4: Connect Domain

### 4.1 Configure Domain in Render/Fly.io

**For Render:**
1. In Render dashboard, go to your web service
2. Click "Settings" → "Custom Domains"
3. Add `api.verifai.tech`
4. Render will provide DNS records

**For Fly.io:**
```bash
fly certs add api.verifai.tech
```

### 4.2 Update Namecheap DNS

In your Namecheap domain settings, add these records:

```
Type: CNAME
Name: api
Value: your-app-name.onrender.com (or .fly.dev)
TTL: 300
```

### 4.3 Update Frontend API URL

Update your frontend config to use the custom domain:

```javascript
API_BASE_URL = "https://api.verifai.tech";
```

## 📧 Step 5: Configure Email

### 5.1 Gmail App Password

1. Go to Google Account settings
2. Enable 2-factor authentication
3. Generate an App Password for "Mail"
4. Use this password in your `EMAIL_HOST_PASSWORD` environment variable

### 5.2 Test Email Functionality

1. Sign up a test user
2. Submit a model/dataset through the Services page
3. Check if email is received at `info.verifai@gmail.com`

## 🔒 Step 6: Security & Performance

### 6.1 SSL Certificate

Both Render and Fly.io automatically provide SSL certificates.

### 6.2 Database Backups

- **Render**: Automatic backups included
- **Fly.io**: Manual backups available

### 6.3 Monitoring

Both platforms provide basic monitoring and logs.

## 🧪 Step 7: Testing

### 7.1 Test User Registration

1. Visit your frontend URL
2. Try to register a new user
3. Verify the user is created in the database

### 7.2 Test File Upload

1. Log in with a test user
2. Upload a model and dataset
3. Verify the email is sent with user information

### 7.3 Test Services Page

1. Go to the Services page
2. Submit an evaluation request
3. Verify the email includes user details

## 📊 Step 8: Monitoring & Maintenance

### 8.1 Platform Dashboards

- **Render**: Monitor usage, logs, and deployment status
- **Fly.io**: Use `fly status` and `fly logs` commands

### 8.2 Database Management

- **Render**: Access through dashboard
- **Fly.io**: Use `fly postgres connect`

### 8.3 Updates

- Push changes to GitHub
- Automatic redeployment
- Monitor for any issues

## 🆘 Troubleshooting

### Common Issues

1. **CORS Errors**: Check CORS_ALLOWED_ORIGINS in settings
2. **Database Connection**: Verify DATABASE_URL is set
3. **Email Not Sending**: Check Gmail app password
4. **Static Files**: Ensure STATIC_ROOT is configured

### Useful Commands

**For Render:**
- Check logs in the dashboard
- Environment variables in dashboard

**For Fly.io:**
```bash
fly logs
fly ssh console
fly postgres connect
```

## 💰 Cost Breakdown: $0 TOTAL

- **Render**: Free tier (750 hours/month)
- **Fly.io**: Free tier (3 shared-cpu VMs)
- **PostgreSQL**: Free tier included
- **Domain**: Your existing Namecheap domain
- **Email**: Gmail (free)
- **Frontend**: GitHub Pages/Vercel (free)

## 🎉 Success!

Your VerifAI application is now deployed with:
- ✅ User authentication (signup/signin)
- ✅ File upload functionality
- ✅ Email notifications with user details
- ✅ Custom domain support (api.verifai.tech)
- ✅ SSL certificates
- ✅ Database persistence
- ✅ Automatic deployments
- ✅ **100% FREE** - No monthly payments!

Users can now register, log in, and submit evaluation requests that will be emailed to your team with their contact information! 