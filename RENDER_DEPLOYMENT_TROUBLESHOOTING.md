# Render Deployment Troubleshooting Guide

## 🚨 Common Issues and Solutions

### 1. OpenAI Connection Errors

**Symptoms:**
```
AI response generation failed: Connection error
openai._base_client - INFO - Retrying request to /chat/completions
```

**Root Causes & Solutions:**

#### Missing API Key
- **Problem**: `OPENAI_API_KEY` not set in Render environment variables
- **Solution**: Add the environment variable in Render dashboard
- **Check**: Verify the key is valid and has sufficient credits

#### Network Timeouts
- **Problem**: Default timeout too short for Render's network
- **Solution**: Increase `OPENAI_TIMEOUT` to 60+ seconds
- **Configuration**: Set `OPENAI_TIMEOUT=60.0` in environment variables

#### Rate Limiting
- **Problem**: Too many requests to OpenAI API
- **Solution**: Implement exponential backoff (already included)
- **Monitor**: Check OpenAI usage dashboard

### 2. Environment Variable Configuration

**Required Variables for Render:**
```yaml
ENVIRONMENT=production
OPENAI_API_KEY=your_actual_key_here
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TIMEOUT=60.0
OPENAI_MAX_RETRIES=3
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
PROPERTY_ADDRESS=123 Luxury Lane, Downtown District, NY 10001
PROPERTY_NAME=Luxury Apartments at Main Street
LEASING_OFFICE_PHONE=(555) 123-4567
FRONTEND_URL=https://your-frontend.onrender.com
```

### 3. Deployment Steps

1. **Update render.yaml** with all required environment variables
2. **Set sensitive variables** in Render dashboard (marked with `sync: false`)
3. **Deploy** and monitor logs for connection issues
4. **Test** the chat functionality end-to-end

### 4. Monitoring and Debugging

#### Check Logs
```bash
# In Render dashboard, view service logs for:
- "AI service initialized with model: gpt-3.5-turbo"
- "OpenAI API key not configured" (indicates missing key)
- Connection error patterns
```

#### Test AI Service
```bash
# Local testing before deployment
cd backend
python -c "
import os
from ai_service import AIService
ai = AIService()
print(f'AI enabled: {ai.enabled}')
print(f'Model: {ai.model}')
"
```

### 5. Performance Optimization

#### Timeout Settings
- **Development**: 30 seconds
- **Production**: 60+ seconds (Render has higher latency)
- **Heavy Load**: Consider 90+ seconds

#### Retry Configuration
- **Max Retries**: 3 attempts
- **Backoff**: Exponential (1s, 2s, 4s)
- **Rate Limits**: Graceful degradation

### 6. Fallback Behavior

When AI is unavailable, the system:
- ✅ Continues core booking functionality
- ✅ Provides helpful error messages
- ✅ Maintains conversation state
- ✅ Logs issues for debugging

### 7. Quick Fixes

#### Immediate Actions
1. Check Render environment variables
2. Verify OpenAI API key validity
3. Increase timeout values
4. Monitor OpenAI usage/billing

#### Emergency Fallback
```python
# Temporarily disable AI if needed
OPENAI_API_KEY=disabled
# System will gracefully fall back to basic responses
```

## 🔧 Deployment Checklist

- [ ] All environment variables set in render.yaml
- [ ] Sensitive variables configured in Render dashboard
- [ ] OpenAI API key valid and funded
- [ ] Timeout values appropriate for production
- [ ] Frontend URL correctly configured
- [ ] Email service credentials valid
- [ ] Health check endpoint responding
- [ ] End-to-end chat flow tested

## 📞 Support

If issues persist:
1. Check OpenAI status page
2. Verify Render service status
3. Review application logs
4. Test with minimal configuration
5. Contact support with specific error messages

---

**Last Updated**: 2024-06-04
**Version**: 1.0.0
