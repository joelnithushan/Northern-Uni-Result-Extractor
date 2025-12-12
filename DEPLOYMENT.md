# Deployment Guide

## Option 1: Railway (Recommended - Free Tier Available)

1. **Sign up/Login to Railway:**
   - Go to https://railway.app
   - Sign up with GitHub

2. **Deploy:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository: `Northern-Uni-Result-Extractor`
   - Railway will automatically detect it's a Python app

3. **Configure:**
   - Railway will automatically use the `Procfile`
   - The app will be deployed and you'll get a URL like: `https://your-app-name.railway.app`

4. **Done!** Your app is live.

---

## Option 2: Render (Free Tier Available)

1. **Sign up/Login to Render:**
   - Go to https://render.com
   - Sign up with GitHub

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `Northern-Uni-Result-Extractor`

3. **Configure:**
   - **Name:** northern-uni-result-extractor (or your choice)
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python app.py`
   - **Plan:** Free

4. **Deploy:**
   - Click "Create Web Service"
   - Render will build and deploy your app
   - You'll get a URL like: `https://your-app-name.onrender.com`

---

## Option 3: PythonAnywhere (Free Tier Available)

1. **Sign up:** https://www.pythonanywhere.com

2. **Upload files:**
   - Go to Files tab
   - Upload `app.py`, `requirements.txt`, and `templates/` folder

3. **Install dependencies:**
   - Go to Bash console
   - Run: `pip3.10 install --user -r requirements.txt`

4. **Configure Web App:**
   - Go to Web tab
   - Click "Add a new web app"
   - Choose Flask and Python 3.10
   - Set source file to: `/home/yourusername/app.py`
   - Set working directory to: `/home/yourusername/`

5. **Reload:** Click the reload button

---

## Environment Variables (if needed)

Most platforms don't require any environment variables for this app, but if you need to set PORT:
- **Railway/Render:** Automatically sets PORT
- **Manual:** Set `PORT=5000` (or your preferred port)

---

## Notes

- The `uploads/` folder is created automatically
- PDF files are processed in memory, so no persistent storage needed
- Free tiers may have limitations on request timeouts (usually 30-60 seconds)

