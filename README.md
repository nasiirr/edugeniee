# 🧠 Edugenie - AI-Powered Educational Assistant

An intelligent learning platform that generates personalized quizzes and study materials using Google's Gemini AI.

## 🌟 Features

### Quiz Generation System
- 📝 **Personalized Quizzes** - Generate quizzes on any topic
- 🎯 **Bloom's Taxonomy** - Questions aligned with educational levels
- 📊 **Learning Analytics** - Track your progress and performance
- ✅ **Multiple Question Types** - MCQ, True/False, and Short Answer
- 💡 **Detailed Explanations** - Learn from your mistakes

### Study Material Generator
- 📚 **Multiple Formats** - Summaries, Flashcards, Comprehensive Notes
- 👥 **Adaptive Content** - Tailored to your education level
- 💾 **Personal Library** - Save and access materials anytime
- ⏱️ **Reading Time Estimates** - Plan your study sessions

## 🚀 Live Demo

[Deploy on Streamlit Cloud](https://edugeniee.streamlit.app/)

## 🛠️ Technology Stack

- **Frontend:** Streamlit
- **AI Engine:** Google Gemini API
- **Database:** Firebase Firestore
- **Language:** Python 3.8+

## 📦 Installation

1. Clone the repository:
\`\`\`bash
git clone <your-repo-url>
cd streamlit
\`\`\`

2. Install dependencies:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Set up environment variables:
Create a \`.env\` file with:
\`\`\`
GEMINI_API_KEY=your_gemini_api_key
FIREBASE_CREDENTIALS_PATH=serviceAccount.json
\`\`\`

4. Run the application:
\`\`\`bash
streamlit run app.py
\`\`\`

## ☁️ Deployment on Streamlit Cloud

1. Push your code to GitHub (without .env and serviceAccount.json)
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Connect your GitHub repository
4. Add secrets in the secrets management section (see below)
5. Deploy!

### Secrets Configuration

In Streamlit Cloud secrets (TOML format):

\`\`\`toml
GEMINI_API_KEY = "your_gemini_api_key"

[firebase_credentials]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\\nYour\\nKey\\nHere\\n-----END PRIVATE KEY-----\\n"
client_email = "your-service-account@project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "your-cert-url"
\`\`\`

## 🔑 Getting API Keys

### Gemini API Key
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy and add to secrets

### Firebase Setup
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project
3. Enable Firestore Database
4. Go to Project Settings → Service Accounts
5. Generate a new private key (downloads JSON)
6. Copy the JSON contents to secrets

## 📁 Project Structure

\`\`\`
streamlit/
├── app.py                    # Main quiz application
├── pages/
│   └── content_generator.py  # Study material generator
├── requirements.txt          # Python dependencies
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── .gitignore               # Git ignore rules
└── README.md                # This file
\`\`\`

## 🎓 Usage

### Quiz Generation
1. Enter a topic (e.g., "Solar System")
2. Select Bloom's Taxonomy level
3. Choose number of questions (1-20)
4. Select question type
5. Click "Generate Quiz"
6. Take the quiz and review results

### Study Material Generation
1. Navigate to "Study Material Generator" page
2. Enter topic and select parameters
3. Click "Generate Content"
4. Review the generated material
5. Save to your library for later access

## 📊 Features in Detail

- **Bloom's Taxonomy Levels:** Remember, Understand, Apply, Analyze, Evaluate, Create
- **Question Types:** Multiple Choice, True/False, Short Answer
- **Study Material Types:** Summaries, Flashcards, Comprehensive Notes
- **Target Audiences:** High School, Undergraduate, Graduate, Self-learner

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License.

## 👨‍💻 Author

Created by NASIR

## 🙏 Acknowledgments

- Google Gemini AI for content generation
- Streamlit for the amazing framework
- Firebase for database services
