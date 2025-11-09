# Quick Deployment Checklist for Streamlit Cloud

## ✅ Pre-Deployment Checklist

- [ ] Code is working locally
- [ ] `.gitignore` file exists (don't commit secrets!)
- [ ] `requirements.txt` is up to date
- [ ] GitHub repository created
- [ ] Gemini API key ready
- [ ] Firebase serviceAccount.json file ready

---

## 📋 Step-by-Step Instructions

### 1. Push to GitHub (FIRST TIME)

\`\`\`bash
# Initialize git (if not already done)
git init

# Add all files (sensitive files will be ignored by .gitignore)
git add .

# Commit
git commit -m "Initial commit for Edugenie app"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
\`\`\`

**⚠️ VERIFY:** Check GitHub to ensure `.env` and `serviceAccount.json` are NOT uploaded!

---

### 2. Prepare Your Secrets

**A. Get Gemini API Key:**
- Open your `.env` file
- Copy the value of `GEMINI_API_KEY`
- Example: `AIzaSyC...your_key_here`

**B. Get Firebase Credentials:**
- Open your `serviceAccount.json` file
- You'll need to convert it to TOML format

**Use this Python script to convert:**

\`\`\`python
import json

# Read your serviceAccount.json
with open('serviceAccount.json', 'r') as f:
    data = json.load(f)

# Print TOML format for Streamlit secrets
print("# Copy everything below and paste into Streamlit Cloud secrets:")
print()
print(f'GEMINI_API_KEY = "YOUR_GEMINI_KEY_HERE"')
print()
print("[firebase_credentials]")
for key, value in data.items():
    if isinstance(value, str):
        # Escape newlines in private_key
        if key == 'private_key':
            value = value.replace('\\n', '\\\\n')
        print(f'{key} = "{value}"')
    else:
        print(f'{key} = {value}')
\`\`\`

Save this as `convert_secrets.py` and run: `python convert_secrets.py`

---

### 3. Deploy on Streamlit Cloud

1. **Go to:** https://share.streamlit.io/

2. **Sign in** with GitHub

3. **Click:** "New app" button

4. **Fill in details:**
   - Repository: `YOUR_USERNAME/YOUR_REPO_NAME`
   - Branch: `main`
   - Main file path: `app.py`

5. **Click:** "Advanced settings..."

6. **Paste your secrets** in TOML format:

\`\`\`toml
GEMINI_API_KEY = "AIzaSyC...your_actual_key"

[firebase_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\\nYour\\nKey\\nHere\\n-----END PRIVATE KEY-----\\n"
client_email = "your-email@project.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
\`\`\`

7. **Click:** "Deploy!"

8. **Wait** 2-3 minutes for deployment

9. **Your app will be live at:** `https://YOUR-APP-NAME.streamlit.app`

---

## 🔄 Updating Your Deployed App

After initial deployment, any changes you push to GitHub will auto-deploy:

\`\`\`bash
# Make your changes to the code
# Then:
git add .
git commit -m "Description of changes"
git push
\`\`\`

Streamlit Cloud will automatically detect changes and redeploy!

---

## 🐛 Troubleshooting

### App won't start
- Check logs in Streamlit Cloud dashboard
- Verify all dependencies in `requirements.txt`
- Ensure Python version compatibility

### "API key not found" error
- Go to App settings → Secrets
- Verify `GEMINI_API_KEY` is spelled correctly
- No extra spaces or quotes

### Firebase error
- Check all firebase_credentials fields are present
- Verify `private_key` has `\\\\n` (double backslash-n)
- Ensure Firebase project has Firestore enabled

### Module not found
- Update `requirements.txt`:
  \`\`\`bash
  pip freeze > requirements.txt
  git add requirements.txt
  git commit -m "Update dependencies"
  git push
  \`\`\`

---

## 📱 Accessing Your Deployed App

**Your app URL will be:**
- https://YOUR-APP-NAME.streamlit.app
- Or: https://CUSTOM-SUBDOMAIN.streamlit.app

**Share with:**
- Students
- Teachers  
- On your resume
- In your project report

---

## 🎉 Success Indicators

✅ App loads without errors
✅ Quiz generation works
✅ Study material generation works
✅ Firebase saves data successfully
✅ User stats display correctly

---

## 💡 Pro Tips

1. **Custom domain:** Streamlit allows custom domains on paid plans
2. **Analytics:** Enable Streamlit analytics to see usage stats
3. **Private apps:** Make repo private (requires Streamlit paid plan)
4. **Monitoring:** Check app logs regularly for errors
5. **Updates:** Test locally before pushing to production

---

## 🆘 Need Help?

- **Streamlit Community:** https://discuss.streamlit.io/
- **Documentation:** https://docs.streamlit.io/
- **Your GitHub Issues:** Create issues in your repo for tracking

---

Good luck with your deployment! 🚀
