# 🚀 **Vercel Deployment Guide for PhishGuard Pro**

## ✅ **Files Already Configured**

Your project now has all the necessary configuration files for Vercel deployment:

- ✅ `vercel.json` - Main deployment configuration  
- ✅ Updated `package.json` with build scripts
- ✅ Updated `frontend/vite.config.js` for production
- ✅ Updated `backend/app.py` with serverless handler
- ✅ Updated `.gitignore` for Vercel

## 🚀 **Quick Deployment Steps**

### **Option A: Vercel Dashboard (Recommended)**

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add Vercel deployment configuration"
   git push origin main
   ```

2. **Deploy on Vercel:**
   - Go to [vercel.com](https://vercel.com) and login
   - Click "New Project"
   - Import your GitHub repository
   - Configure:
     - **Framework Preset**: Other
     - **Root Directory**: . (leave empty)
     - **Build Command**: `npm run vercel-build`
     - **Output Directory**: `frontend/dist`

3. **Set Environment Variables:**
   - Go to Project → Settings → Environment Variables
   - Add: `GEMINI_API_KEY` = your_actual_gemini_api_key_here
   - Add: `NODE_ENV` = production

4. **Deploy!**
   - Click "Deploy"
   - Wait for deployment to complete

### **Option B: Vercel CLI**

1. **Install Vercel CLI:**
   ```bash
   npm i -g vercel
   ```

2. **Login and Deploy:**
   ```bash
   vercel login
   vercel
   ```

3. **Set Environment Variables:**
   ```bash
   vercel env add GEMINI_API_KEY
   # Enter your actual Gemini API key
   
   vercel env add NODE_ENV
   # Enter: production
   ```

4. **Deploy to Production:**
   ```bash
   vercel --prod
   ```

## 🔧 **After First Deployment**

1. **Update Frontend API URL:**
   - Note your Vercel URL (e.g., `https://phishguard-pro.vercel.app`)
   - Update `frontend/vite.config.js` line 15 with your actual URL
   - Commit and push changes

2. **Test Your Application:**
   - Frontend: Visit your Vercel URL
   - API: Test `https://your-url.vercel.app/api/status`
   - Full Test: Try analyzing `bit.ly/amazon-deal`

## 🎯 **What's Deployed**

- ✅ **React Frontend** - Static files served by Vercel CDN
- ✅ **Flask Backend** - Serverless functions with Google Gemini AI
- ✅ **Single Domain** - Frontend and API on same URL
- ✅ **Automatic HTTPS** - SSL certificates included
- ✅ **Global CDN** - Fast worldwide access

## 🐛 **Troubleshooting**

### **Common Issues:**
- **Build Fails**: Check that `frontend/package.json` dependencies are correct
- **API Errors**: Verify `GEMINI_API_KEY` environment variable is set
- **CORS Issues**: Backend CORS is configured for all origins

### **Logs & Debugging:**
- View deployment logs in Vercel dashboard
- Check function logs for API errors
- Test API endpoints directly

## ✨ **Success!**

Your PhishGuard Pro application is now deployed with:
- 🌐 Global CDN for fast loading
- 🔒 Automatic HTTPS security  
- ⚡ Serverless scaling
- 🤖 Google Gemini AI integration
- 🛡️ Advanced phishing detection

**Live URL**: `https://your-project-name.vercel.app`
