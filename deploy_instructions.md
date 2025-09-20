# PhishGuard Deployment Guide

## 🚀 Quick Local Deployment

### Windows (Easiest)
1. **Double-click** `deploy_local.bat`
2. Access the application at `http://localhost:5173`

### Manual Local Deployment
```bash
# Terminal 1 - Start Backend
cd backend
python app.py

# Terminal 2 - Start Frontend  
cd frontend
npm run dev
```

## 🌐 Production Deployment Options

### Option 1: Docker (Recommended)

#### Prerequisites
- Docker & Docker Compose installed
- Valid Gemini API key

#### Steps
```bash
# 1. Set your API key
echo "GEMINI_API_KEY=your_actual_api_key_here" > backend/.env

# 2. Build and run
docker-compose up -d

# 3. Access application
# http://localhost:5001 (direct backend)
# http://localhost:80 (with nginx proxy)
```

### Option 2: VPS/Cloud Server

#### On Ubuntu/Debian Server
```bash
# 1. Install dependencies
sudo apt update
sudo apt install python3 python3-pip nodejs npm nginx

# 2. Clone your project
git clone <your-repo-url>
cd PhishGuard

# 3. Setup backend
cd backend
pip3 install -r requirements.txt
pip3 install gunicorn

# 4. Setup frontend
cd ../frontend
npm install
npm run build

# 5. Configure environment
echo "GEMINI_API_KEY=your_actual_api_key_here" > backend/.env

# 6. Run with gunicorn
cd backend
gunicorn --config gunicorn_config.py wsgi:app
```

### Option 3: Cloud Platforms

#### Heroku
```bash
# 1. Install Heroku CLI
# 2. Create Heroku app
heroku create your-phishguard-app

# 3. Set environment variables
heroku config:set GEMINI_API_KEY=your_actual_api_key_here

# 4. Deploy
git push heroku main
```

#### Railway/Render
1. Connect your GitHub repository
2. Set environment variable: `GEMINI_API_KEY`
3. Deploy automatically

#### AWS/GCP/Azure
- Use the Docker deployment method
- Deploy to container services (ECS, Cloud Run, Container Instances)

## 🔧 Environment Configuration

### Required Environment Variables
```bash
# Backend (.env file)
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=production
FLASK_DEBUG=false
```

### Frontend Configuration
Update `frontend/vite.config.js` for production:
```javascript
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://your-backend-domain.com',  // Update for production
        changeOrigin: true,
      },
    },
  },
})
```

## 🛡️ Security Considerations

### For Production
1. **HTTPS**: Use SSL certificates (Let's Encrypt recommended)
2. **Rate Limiting**: Configure nginx or use CloudFlare
3. **API Key Security**: Never expose your Gemini API key
4. **CORS**: Configure proper CORS settings for your domain
5. **Firewall**: Restrict access to necessary ports only

### Security Headers (already included in nginx.conf)
- X-Content-Type-Options
- X-Frame-Options  
- X-XSS-Protection
- Strict-Transport-Security

## 📊 Monitoring & Health Checks

### Health Check Endpoint
```bash
curl http://your-domain.com/api/status
```

Response:
```json
{
  "service": "PhishGuard API",
  "status": "running", 
  "ai_enabled": true,
  "ai_service": "Google Gemini",
  "version": "2.0.0-ai"
}
```

## 🐛 Troubleshooting

### Common Issues
1. **API Key Error**: Ensure `GEMINI_API_KEY` is set correctly
2. **CORS Issues**: Update frontend proxy configuration  
3. **Port Conflicts**: Change ports in configuration files
4. **Dependencies**: Run `pip install -r requirements.txt`

### Logs
```bash
# Docker logs
docker-compose logs -f

# Backend logs  
tail -f backend/app.log

# Nginx logs
tail -f /var/log/nginx/access.log
```

## 📈 Scaling

### Horizontal Scaling
- Use multiple backend instances behind a load balancer
- Scale Docker containers: `docker-compose up --scale phishguard=3`

### Performance Optimization
- Enable gzip compression in nginx
- Use CDN for static assets
- Implement Redis for caching (if needed)
- Monitor response times and optimize accordingly

## 🔄 Updates & Maintenance

### Updating the Application
```bash
# Pull latest changes
git pull origin main

# Rebuild and redeploy
docker-compose down
docker-compose up --build -d
```

### Backup Strategy
- Backup your `.env` file securely
- Version control your configuration files
- Monitor API usage and costs
