# Deployment Guide

## Deploying to Render

### Backend Deployment
1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `SMTP_EMAIL`: Your Gmail address
   - `SMTP_PASSWORD`: Your Gmail app password
   - `PROPERTY_ADDRESS`: Your property address
   - `FRONTEND_URL`: Your frontend URL (after deploying frontend)

### Frontend Deployment
1. Create a new Static Site on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/dist`
4. Add environment variable:
   - `VITE_API_URL`: Your backend URL from above

### Post-Deployment
1. Update your backend's `FRONTEND_URL` environment variable
2. Test the chat flow end-to-end