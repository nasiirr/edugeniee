# 🚀 Deployment Guide for Edugenie

## Option 1: Streamlit Community Cloud (RECOMMENDED - FREE)

### Prerequisites
- GitHub account
- Your code pushed to a GitHub repository
- Gemini API key
- Firebase service account JSON

### Step-by-Step Deployment

#### 1. Prepare Your Repository

Make sure you have:
- ✅ `.gitignore` file (to exclude sensitive files)
- ✅ `requirements.txt` with all dependencies
- ✅ Code pushed to GitHub **WITHOUT** `.env` or `serviceAccount.json`

#### 2. Get Your Secrets Ready

**A. Gemini API Key**
- Copy your `GEMINI_API_KEY` value

**B. Firebase Credentials**
- Open your `serviceAccount.json` file
- You'll need all the fields for the secrets configuration

#### 3. Deploy on Streamlit Cloud

1. **Go to:** https://share.streamlit.io/

2. **Sign in** with your GitHub account

3. **Click "New app"**

4. **Configure deployment:**
   - Repository: Select your repo
   - Branch: `main` (or your default branch)
   - Main file path: `app.py`

5. **Click "Advanced settings"**

6. **Add secrets** in the TOML format:

\`\`\`toml
# Copy your Gemini API key here
GEMINI_API_KEY = "AIza...your_actual_key_here"

# Copy all fields from your serviceAccount.json
[firebase_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\\nMIIEvQIBADANBg...your_key...\\n-----END PRIVATE KEY-----\\n"
client_email = "firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com"
universe_domain = "googleapis.com"
\`\`\`

⚠️ **IMPORTANT:** 
- Replace all placeholder values with your actual credentials
- The `private_key` field must have `\\n` (double backslash + n) for line breaks
- Don't add quotes around the entire TOML block, only around individual values

7. **Click "Deploy"**

8. **Wait for deployment** (usually 2-3 minutes)

9. **Access your app** at: `https://your-app-name.streamlit.app`

### Troubleshooting Streamlit Cloud

**Error: "GEMINI_API_KEY not found"**
- Check that you spelled `GEMINI_API_KEY` correctly in secrets
- Ensure there are no extra spaces

**Error: "Firebase initialization failed"**
- Verify all firebase_credentials fields are present
- Check that `private_key` has proper `\\n` escaping
- Make sure the service account has Firestore permissions

**App crashes on startup**
- Check the logs in Streamlit Cloud dashboard
- Verify `requirements.txt` has all dependencies

---

## Option 2: Render (FREE with limitations)

### Prerequisites
- GitHub account
- Code pushed to GitHub

### Deployment Steps

1. **Go to:** https://render.com/

2. **Sign up** and connect GitHub

3. **Create New Web Service**

4. **Connect repository**

5. **Configure:**
   - Name: `edugenie`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true`

6. **Add Environment Variables:**
   - `GEMINI_API_KEY`: Your Gemini API key
   - `FIREBASE_CREDENTIALS_JSON`: Entire serviceAccount.json content as a single-line string

7. **Deploy**

**Note:** Free tier sleeps after 15 minutes of inactivity.

---

## Option 3: Railway

### Prerequisites
- GitHub account

### Deployment Steps

1. **Go to:** https://railway.app/

2. **Sign up** with GitHub

3. **New Project** → **Deploy from GitHub repo**

4. **Select repository**

5. **Add Environment Variables:**
   - `GEMINI_API_KEY`
   - `FIREBASE_CREDENTIALS_JSON`

6. **Add Start Command:**
   \`\`\`
   streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   \`\`\`

7. **Deploy**

**Cost:** $5 free credit/month, then ~$5/month

---

## Option 4: Google Cloud Run (Scalable)

### Prerequisites
- Google Cloud account
- Docker installed locally
- gcloud CLI installed

### Deployment Steps

1. **Create Dockerfile:**

\`\`\`dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

CMD streamlit run app.py --server.port=8080 --server.address=0.0.0.0 --server.headless=true
\`\`\`

2. **Build and deploy:**

\`\`\`bash
gcloud run deploy edugenie \\
  --source . \\
  --platform managed \\
  --region us-central1 \\
  --allow-unauthenticated \\
  --set-env-vars GEMINI_API_KEY=your_key \\
  --set-env-vars FIREBASE_CREDENTIALS_JSON='{"type":"service_account",...}'
\`\`\`

---

## Comparison Table

| Platform | Cost | Ease | Performance | Best For |
|----------|------|------|-------------|----------|
| **Streamlit Cloud** | ✅ Free | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Public projects, demos |
| **Render** | ⚠️ Limited free | ⭐⭐⭐⭐ | ⭐⭐⭐ | Small apps |
| **Railway** | 💰 ~$5/mo | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Production apps |
| **Google Cloud Run** | 💰 Pay per use | ⭐⭐ | ⭐⭐⭐⭐⭐ | Enterprise apps |
| **Hugging Face** | ✅ Free | ⭐⭐⭐ | ⭐⭐ | ML demos only |

---

## 🎯 Recommendation

**For your project: Use Streamlit Community Cloud**

✅ **Why?**
- Completely FREE for public repos
- Built specifically for Streamlit apps
- Easy secrets management
- Auto-deployment on git push
- Perfect for educational projects
- No Docker knowledge needed
- Great performance

---

## 📝 Secrets Template

Save this template and fill in your actual values:

\`\`\`toml
# Gemini API Key
GEMINI_API_KEY = "YOUR_ACTUAL_GEMINI_API_KEY"

# Firebase Service Account
[firebase_credentials]
type = "service_account"
project_id = "YOUR_PROJECT_ID"
private_key_id = "YOUR_PRIVATE_KEY_ID"
private_key = "-----BEGIN PRIVATE KEY-----\\nYOUR_PRIVATE_KEY_HERE\\n-----END PRIVATE KEY-----\\n"
client_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
client_id = "YOUR_CLIENT_ID"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "YOUR_CERT_URL"
\`\`\`

---

## 🆘 Need Help?

- **Streamlit Docs:** https://docs.streamlit.io/streamlit-community-cloud
- **Streamlit Forum:** https://discuss.streamlit.io/
- **Firebase Docs:** https://firebase.google.com/docs

Good luck with your deployment! 🚀
