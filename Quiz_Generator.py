import streamlit as st
import google.generativeai as genai
import re
import os
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception:
    firebase_admin = None

# --- Configuration ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or st.secrets.get('GEMINI_API_KEY', '')
if not GEMINI_API_KEY:
    st.error("⚠️ GEMINI_API_KEY not found. Please configure it in .env or Streamlit secrets.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

st.set_page_config(
    page_title="Quiz Generation - Edugenie",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state
if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False

def parse_quiz(quiz_text, question_type):
    """Parses the generated text to extract questions, options, answers, and explanations."""
    questions = []
    
    if question_type == 'Multiple Choice':
        # Split by question numbers and process each
        parts = re.split(r'\n(?=\d+\.)', quiz_text.strip())
        for part in parts:
            if not part.strip():
                continue
                
            lines = part.strip().split('\n')
            question_line = ""
            options = []
            answer = ""
            explanation = ""
            
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line and (line[0].isdigit() or line.startswith('Question')):
                    question_line = line
                elif line.startswith(('A.', 'B.', 'C.', 'D.')):
                    options.append(line)
                elif 'Answer' in line or 'Correct' in line:
                    answer = line.split(':')[-1].strip() if ':' in line else line
                elif 'Explanation' in line:
                    explanation = line.split(':', 1)[-1].strip() if ':' in line else ""
                    # Get remaining lines as part of explanation
                    while i + 1 < len(lines) and not lines[i + 1].strip().startswith(('Answer', 'Correct', '1.', '2.', '3.', '4.', '5.')):
                        i += 1
                        explanation += " " + lines[i].strip()
                i += 1
            
            if question_line and len(options) >= 4:
                questions.append({
                    "question": question_line,
                    "options": options,
                    "answer": answer,
                    "explanation": explanation
                })
    
    elif question_type == 'True/False':
        parts = re.split(r'\n(?=\d+\.)', quiz_text.strip())
        for part in parts:
            if not part.strip():
                continue
                
            lines = part.strip().split('\n')
            question_line = ""
            answer = ""
            explanation = ""
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('Question')):
                    question_line = line
                elif 'Answer' in line or 'Correct' in line:
                    answer = line.split(':')[-1].strip() if ':' in line else line
                elif 'Explanation' in line:
                    explanation = line.split(':', 1)[-1].strip() if ':' in line else ""
            
            if question_line:
                questions.append({
                    "question": question_line,
                    "options": ["True", "False"],
                    "answer": answer,
                    "explanation": explanation
                })
    
    elif question_type == 'Short Answer':
        parts = re.split(r'\n(?=\d+\.)', quiz_text.strip())
        for part in parts:
            if not part.strip():
                continue
                
            lines = part.strip().split('\n')
            question_line = ""
            answer = ""
            explanation = ""
            
            for i, line in enumerate(lines):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('Question')):
                    question_line = line
                elif 'Answer' in line or 'Correct' in line:
                    answer = line.split(':')[-1].strip() if ':' in line else line
                elif 'Explanation' in line:
                    explanation = line.split(':', 1)[-1].strip() if ':' in line else ""
            
            if question_line:
                questions.append({
                    "question": question_line,
                    "options": [],
                    "answer": answer,
                    "explanation": explanation
                })
    
    return questions

def reset_quiz():
    """Reset all quiz-related session state"""
    st.session_state.quiz_generated = False
    st.session_state.quiz_questions = []
    st.session_state.current_question = 0
    st.session_state.user_answers = {}
    st.session_state.quiz_completed = False
    st.session_state.quiz_started = False

def init_firestore():
    """Initialize Firestore client"""
    if firebase_admin is None:
        return None, "firebase-admin not installed"

    try:
        app = None
        try:
            app = firebase_admin.get_app()
        except ValueError:
            pass

        if app is None:
            cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
            cred_json = os.getenv('FIREBASE_CREDENTIALS_JSON')
            
            try:
                if 'firebase_credentials' in st.secrets:
                    cred_dict = dict(st.secrets['firebase_credentials'])
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                elif cred_json:
                    cred_dict = json.loads(cred_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                elif cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    return None, "No Firebase credentials found"
            except Exception:
                return None, "Firebase initialization failed"

        db = firestore.client()
        return db, None
    except Exception as e:
        return None, str(e)

def save_quiz_attempt(db, topic, blooms_level, total_questions, correct_answers, score_percentage, questions_data, user_id='default_user'):
    """Save quiz attempt with all questions to Firestore"""
    try:
        attempt_data = {
            'user_id': user_id,
            'topic': topic,
            'blooms_level': blooms_level,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'score_percentage': score_percentage,
            'timestamp': datetime.datetime.utcnow(),
            'created_at': datetime.datetime.utcnow()
        }
        
        # Create the quiz attempt document
        attempt_ref = db.collection('quiz_attempts').document()
        attempt_ref.set(attempt_data)
        
        # Save each question as a subcollection
        for idx, question in enumerate(questions_data):
            question_doc = {
                'question_number': idx + 1,
                'question_text': question.get('question', ''),
                'options': question.get('options', []),
                'correct_answer': question.get('answer', ''),
                'explanation': question.get('explanation', ''),
                'user_answer': question.get('user_answer', ''),
                'is_correct': question.get('is_correct', False),
                'created_at': datetime.datetime.utcnow()
            }
            attempt_ref.collection('questions').add(question_doc)
        
        return True
    except Exception as e:
        st.error(f"Failed to save quiz attempt: {e}")
        return False

def get_user_insights(db, user_id='default_user'):
    """Get user insights from Firestore"""
    try:
        attempts_ref = db.collection('quiz_attempts').where('user_id', '==', user_id).limit(100)
        attempts = list(attempts_ref.stream())
        
        if not attempts:
            return None
        
        total_attempts = len(attempts)
        total_questions = 0
        correct_answers = 0
        recent_scores = []
        
        for attempt in attempts:
            data = attempt.to_dict()
            total_questions += data.get('total_questions', 0)
            correct_answers += data.get('correct_answers', 0)
            recent_scores.append(data.get('score_percentage', 0))
        
        accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 0
        
        return {
            'total_attempts': total_attempts,
            'total_questions': total_questions,
            'correct_answers': correct_answers,
            'accuracy': accuracy,
            'average_score': avg_score,
            'recent_scores': recent_scores[-5:]  # Last 5 scores
        }
    except Exception as e:
        return None

# Main App
st.title("📝 Quiz Generation")
st.markdown("Generate personalized quizzes on any topic with AI-powered questions")

# Sidebar with User Insights
with st.sidebar:
    st.header("📊 Your Learning Stats")
    
    # Try to get insights from Firestore
    db, db_err = init_firestore()
    if db:
        insights = get_user_insights(db)
        if insights:
            st.metric("Total Quizzes", insights['total_attempts'])
            st.metric("Questions Attempted", insights['total_questions'])
            st.metric("Accuracy", f"{insights['accuracy']:.1f}%")
            st.metric("Average Score", f"{insights['average_score']:.1f}%")
            
            if insights['recent_scores']:
                st.subheader("Recent Scores")
                for idx, score in enumerate(reversed(insights['recent_scores']), 1):
                    st.write(f"{idx}. {score:.1f}%")
        else:
            st.info("Complete quizzes to see your stats here!")
    else:
        st.info("📈 Your stats will appear here after completing quizzes")
    
    st.markdown("---")
    st.caption("💡 Keep taking quizzes to improve your stats!")

# Phase 1: Quiz Setup (only show if quiz not generated)
if not st.session_state.quiz_generated:
    st.header("📝 Create Your Quiz")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            topic_input = st.text_input("Topic:", placeholder="e.g., The Solar System", key="topic")
            blooms_taxonomy_level = st.selectbox(
                "Bloom's Taxonomy Level:",
                ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'],
                key="blooms"
            )
        
        with col2:
            num_questions_slider = st.slider("Number of Questions:", min_value=1, max_value=20, value=5, key="num_q")
            question_type_dropdown = st.selectbox(
                "Question Type:",
                ['Multiple Choice', 'True/False'],
                key="q_type"
            )
    
    generate_button = st.button("🚀 Generate Quiz", type="primary", use_container_width=True)
    
    if generate_button:
        if not topic_input:
            st.error("Please enter a topic for the quiz.")
        else:
            with st.spinner("Generating your personalized quiz, please wait..."):
                prompt = f"""
                Generate exactly {num_questions_slider} quiz questions based on these specifications:
                - Topic: {topic_input}
                - Bloom's Taxonomy Level: {blooms_taxonomy_level}
                - Question Type: {question_type_dropdown}

                Format each question exactly as follows:

                1. [Question text here]
                {"A. [Option A]" if question_type_dropdown == 'Multiple Choice' else ""}
                {"B. [Option B]" if question_type_dropdown == 'Multiple Choice' else ""}
                {"C. [Option C]" if question_type_dropdown == 'Multiple Choice' else ""}
                {"D. [Option D]" if question_type_dropdown == 'Multiple Choice' else ""}
                Answer: [Correct answer]
                Explanation: [Detailed explanation]

                {"2. [Next question...]" if num_questions_slider > 1 else ""}

                Make sure to provide exactly {num_questions_slider} complete questions with all required components.
                """

                try:
                    model = genai.GenerativeModel('models/gemini-flash-latest')
                    response = model.generate_content(prompt)
                    quiz_questions = parse_quiz(response.text, question_type_dropdown)
                    
                    if len(quiz_questions) >= 1:
                        st.session_state.quiz_questions = quiz_questions
                        st.session_state.quiz_generated = True
                        st.session_state.quiz_topic = topic_input
                        st.session_state.quiz_type = question_type_dropdown
                        st.session_state.quiz_blooms_level = blooms_taxonomy_level
                        st.session_state.quiz_saved = False  # Reset save flag
                        st.rerun()
                    else:
                        st.error("Failed to generate quiz questions properly. Please try again.")
                        
                except Exception as e:
                    st.error(f"An error occurred while generating the quiz: {e}")
                    st.error("Please check your API key and try again.")

# Phase 2: Take Quiz
elif st.session_state.quiz_generated and not st.session_state.quiz_completed:
    if not st.session_state.quiz_started:
        st.header(f"📚 Quiz Ready: {st.session_state.quiz_topic}")
        st.info(f"**Total Questions:** {len(st.session_state.quiz_questions)} | **Type:** {st.session_state.quiz_type}")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🎯 Start Quiz", type="primary", use_container_width=True):
                st.session_state.quiz_started = True
                st.rerun()
    else:
        # Display current question
        current_q_idx = st.session_state.current_question
        total_questions = len(st.session_state.quiz_questions)
        current_q = st.session_state.quiz_questions[current_q_idx]
        
        # Progress bar
        progress = (current_q_idx + 1) / total_questions
        st.progress(progress)
        st.write(f"Question {current_q_idx + 1} of {total_questions}")
        
        # Question display
        st.subheader(current_q['question'])
        
        # Answer input
        if current_q['options'] and len(current_q['options']) > 0:
            user_answer = st.radio("Choose your answer:", current_q['options'], key=f"q_{current_q_idx}")
        else:
            user_answer = st.text_input("Your answer:", key=f"q_{current_q_idx}")
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_q_idx > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col3:
            if current_q_idx < total_questions - 1:
                if st.button("➡️ Next"):
                    st.session_state.user_answers[current_q_idx] = user_answer
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("✅ Submit Quiz", type="primary"):
                    st.session_state.user_answers[current_q_idx] = user_answer
                    st.session_state.quiz_completed = True
                    st.rerun()

# Phase 3: Show Results
elif st.session_state.quiz_completed:
    st.header("🎉 Quiz Results")
    
    quiz_questions = st.session_state.quiz_questions
    user_answers = st.session_state.user_answers
    score = 0
    
    # Prepare questions data with user answers for Firestore
    questions_data = []
    
    # Calculate score and prepare data
    for i, q in enumerate(quiz_questions):
        user_ans = user_answers.get(i, "")
        correct_ans = q['answer']
        is_correct = False
        
        if q['options']:  # Multiple choice or True/False
            # Extract the letter/option from the correct answer
            if len(correct_ans) > 0:
                if correct_ans.upper().startswith('A') or correct_ans.upper().startswith('B') or correct_ans.upper().startswith('C') or correct_ans.upper().startswith('D'):
                    correct_letter = correct_ans[0].upper()
                    user_letter = user_ans[0].upper() if user_ans else ""
                    if correct_letter == user_letter:
                        score += 1
                        is_correct = True
                elif user_ans.strip().lower() == correct_ans.strip().lower():
                    score += 1
                    is_correct = True
        else:  # Short answer
            if user_ans.strip().lower() == correct_ans.strip().lower():
                score += 1
                is_correct = True
        
        # Prepare question data for Firestore
        questions_data.append({
            'question': q['question'],
            'options': q['options'],
            'answer': q['answer'],
            'explanation': q['explanation'],
            'user_answer': user_ans,
            'is_correct': is_correct
        })
    
    # Display score
    percentage = (score / len(quiz_questions)) * 100
    st.metric("Your Score", f"{score}/{len(quiz_questions)}", f"{percentage:.1f}%")
    
    # Save to Firestore (if not already saved)
    if 'quiz_saved' not in st.session_state or not st.session_state.quiz_saved:
        db, db_err = init_firestore()
        if db:
            topic = st.session_state.get('quiz_topic', 'Unknown')
            blooms_level = st.session_state.get('quiz_blooms_level', 'Unknown')
            
            if save_quiz_attempt(db, topic, blooms_level, len(quiz_questions), score, percentage, questions_data):
                st.session_state.quiz_saved = True
                st.toast("✅ Quiz results saved to your insights!", icon="💾")
        # Don't show error if Firestore is not configured - it's optional
    
    if percentage >= 80:
        st.success("Excellent work! 🌟")
    elif percentage >= 60:
        st.info("Good job! 👍")
    else:
        st.warning("Keep studying! 📚")
    
    # Show detailed results
    st.subheader("📊 Detailed Results")
    
    for i, q in enumerate(quiz_questions):
        with st.expander(f"Question {i+1}: {q['question'][:50]}..."):
            st.write(f"**Question:** {q['question']}")
            
            user_ans = user_answers.get(i, "No answer provided")
            correct_ans = q['answer']
            
            # Check if correct
            is_correct = False
            if q['options']:
                if len(correct_ans) > 0:
                    if correct_ans.upper().startswith('A') or correct_ans.upper().startswith('B') or correct_ans.upper().startswith('C') or correct_ans.upper().startswith('D'):
                        correct_letter = correct_ans[0].upper()
                        user_letter = user_ans[0].upper() if user_ans else ""
                        if correct_letter == user_letter:
                            is_correct = True
                    elif user_ans.strip().lower() == correct_ans.strip().lower():
                        is_correct = True
            else:
                if user_ans.strip().lower() == correct_ans.strip().lower():
                    is_correct = True
            
            if is_correct:
                st.success(f"✅ Your answer: {user_ans}")
            else:
                st.error(f"❌ Your answer: {user_ans}")
                st.info(f"💡 Correct answer: {correct_ans}")
            
            st.write(f"**Explanation:** {q['explanation']}")
    
    # New Quiz button
    st.divider()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔄 Create New Quiz", type="primary", use_container_width=True):
            reset_quiz()
            st.rerun()