# Deployment Guide

## Deploying to Render

### Backend Deployment

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Set the following:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables:
   - `OPENAI_API_KEY`: Your OpenAI API key (required for AI features)
   - `OPENAI_MODEL`: gpt-3.5-turbo (or gpt-4)
   - `OPENAI_TIMEOUT`: 60.0 (recommended for Render)
   - `OPENAI_MAX_RETRIES`: 3
   - `SMTP_EMAIL`: Your Gmail address
   - `SMTP_PASSWORD`: Your Gmail app password
   - `PROPERTY_ADDRESS`: Your property address
   - `PROPERTY_NAME`: Your property name
   - `LEASING_OFFICE_PHONE`: Your phone number
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
3. Monitor logs for any connection errors

### Troubleshooting

If you encounter OpenAI connection errors:

1. **Check Environment Variables**: Ensure `OPENAI_API_KEY` is set correctly
2. **Verify API Key**: Test your key at https://platform.openai.com/playground
3. **Check Billing**: Ensure your OpenAI account has sufficient credits
4. **Monitor Logs**: Look for specific error messages in Render logs
5. **Increase Timeout**: Set `OPENAI_TIMEOUT=60.0` for better reliability

For detailed troubleshooting, see `RENDER_DEPLOYMENT_TROUBLESHOOTING.md`.
