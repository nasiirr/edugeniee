import streamlit as st
import os
import json
import re
import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
except Exception:
    genai = None

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
except Exception:
    firebase_admin = None

# --- Configuration ---
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets.get('GEMINI_API_KEY', '')
    except:
        pass

if GEMINI_API_KEY and genai:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        pass

# Page config
st.set_page_config(page_title="Study Material Generator", page_icon="📚", layout="wide")

# Collection name - PREDEFINED, no user input needed
COLLECTION_NAME = 'study_materials'

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
            except Exception as e:
                if cred_json:
                    cred_dict = json.loads(cred_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                elif cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                else:
                    return None, f"Firebase initialization failed: {str(e)}"

        db = firestore.client()
        return db, None
    except Exception as e:
        return None, str(e)


def parse_questions(quiz_text):
    """Extract questions from generated text"""
    questions = []
    if not quiz_text:
        return questions

    parts = re.split(r'\n(?=\d+\.)', quiz_text.strip())
    for part in parts:
        lines = [l.strip() for l in part.strip().split('\n') if l.strip()]
        if not lines:
            continue

        q_text = lines[0]
        options = []
        answer = ''
        explanation = ''

        for line in lines[1:]:
            if re.match(r'^[A-D]\.', line, re.I):
                options.append(line)
            elif line.lower().startswith('answer') or line.lower().startswith('correct'):
                answer = line.split(':', 1)[-1].strip()
            elif line.lower().startswith('explanation'):
                explanation = line.split(':', 1)[-1].strip()
            else:
                if explanation:
                    explanation += ' ' + line

        questions.append({
            'question': q_text,
            'options': options,
            'answer': answer,
            'explanation': explanation
        })

    return questions


def generate_content(prompt, model_name='gemini-flash-latest'):
    """Generate content using Gemini"""
    if genai is None:
        return None, "google.generativeai not installed"

    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        return response.text, None
    except Exception as e:
        return None, str(e)


def compute_read_time(text):
    """Calculate reading time"""
    words = re.findall(r"\w+", text or '')
    word_count = len(words)
    read_minutes = max(1, round(word_count / 200.0))
    return {
        'word_count': word_count,
        'estimated_read_time_minutes': read_minutes
    }


def save_to_firestore(db, topic, audience, goal, num_items, generated_text, parsed_questions):
    """Save study material to Firestore"""
    try:
        meta = {
            'topic': topic,
            'audience': audience,
            'goal': goal,
            'num_items_requested': num_items,
            'created_at': datetime.datetime.utcnow()
        }
        
        set_ref = db.collection(COLLECTION_NAME).document()
        set_ref.set(meta)

        # Save questions as subcollection
        for q in parsed_questions:
            qdoc = {
                'question': q.get('question', ''),
                'options': q.get('options', []),
                'answer': q.get('answer', ''),
                'explanation': q.get('explanation', ''),
                'created_at': datetime.datetime.utcnow()
            }
            set_ref.collection('questions').add(qdoc)

        # Save raw text
        set_ref.collection('raw').document('generated_text').set({'text': generated_text})

        return True, set_ref.id
    except Exception as e:
        return False, str(e)


def load_saved_materials(db):
    """Load all saved study materials"""
    try:
        study_sets = db.collection(COLLECTION_NAME)\
            .order_by('created_at', direction=firestore.Query.DESCENDING)\
            .limit(20)\
            .stream()
        
        study_sets_list = []
        for doc in study_sets:
            study_sets_list.append({'id': doc.id, **doc.to_dict()})
        
        return study_sets_list, None
    except Exception as e:
        return [], str(e)


# Initialize session state
if 'generated_content' not in st.session_state:
    st.session_state.generated_content = None
if 'content_metadata' not in st.session_state:
    st.session_state.content_metadata = {}
if 'parsed_questions' not in st.session_state:
    st.session_state.parsed_questions = []
if 'show_saved' not in st.session_state:
    st.session_state.show_saved = False

# --- HEADER ---
st.title("📚 Study Material Generator")
st.markdown("*Generate personalized study content and save it to your library*")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Generation Settings")
    
    topic = st.text_input(
        "📖 Topic to Study",
        placeholder="e.g., Machine Learning, Photosynthesis",
        help="Enter the topic you want to study"
    )
    
    audience = st.selectbox(
        "👥 Target Audience",
        ["High School", "Undergraduate", "Graduate", "Self-learner"],
        index=1
    )
    
    goal = st.selectbox(
        "🎯 Study Goal",
        ["Summary", "Flashcards", "Comprehensive Notes"],
        index=0,
        help="Choose what type of content to generate"
    )
    
    num_items = st.slider(
        "📊 Number of Items",
        min_value=1,
        max_value=30,
        value=8,
        help="Number of flashcards/sections to generate"
    )
    
    include_explanations = st.checkbox(
        "💡 Include Explanations",
        value=True,
        help="Add detailed explanations to answers"
    )
    
    st.markdown("---")
    
    # Generate button
    generate_btn = st.button("🚀 Generate Content", type="primary", use_container_width=True)
    
    st.markdown("---")
    
    # Access saved content button
    if st.button("📚 Access Saved Content", use_container_width=True):
        st.session_state.show_saved = True
        st.rerun()
    
    if st.session_state.show_saved:
        if st.button("🔙 Back to Generator", use_container_width=True):
            st.session_state.show_saved = False
            st.rerun()

# --- MAIN CONTENT AREA ---

# Show saved materials view
if st.session_state.show_saved:
    st.header("📚 Your Saved Study Materials")
    
    db, db_err = init_firestore()
    if db is None:
        st.error(f"❌ Firestore not available: {db_err}")
        st.info("💡 Configure Firebase to save and access your study materials")
    else:
        with st.spinner("Loading saved materials..."):
            materials, err = load_saved_materials(db)
            
            if err:
                st.error(f"❌ Error loading materials: {err}")
            elif not materials:
                st.info("📭 No saved materials yet. Generate and save some content first!")
            else:
                st.success(f"✅ Found {len(materials)} saved study material(s)")
                
                for idx, material in enumerate(materials):
                    created_date = material.get('created_at', 'N/A')
                    if hasattr(created_date, 'strftime'):
                        created_date = created_date.strftime('%Y-%m-%d %H:%M')
                    
                    with st.expander(
                        f"📖 **{material.get('topic', 'Untitled')}** - {material.get('goal', 'N/A')} ({created_date})",
                        expanded=(idx == 0)
                    ):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write(f"**Audience:** {material.get('audience', 'N/A')}")
                        with col2:
                            st.write(f"**Goal:** {material.get('goal', 'N/A')}")
                        with col3:
                            st.write(f"**Items:** {material.get('num_items_requested', 'N/A')}")
                        
                        st.markdown("---")
                        
                        # Load raw text
                        try:
                            raw_doc = db.collection(COLLECTION_NAME)\
                                .document(material['id'])\
                                .collection('raw')\
                                .document('generated_text')\
                                .get()
                            
                            if raw_doc.exists:
                                raw_text = raw_doc.to_dict().get('text', '')
                                st.subheader("📄 Content")
                                st.text_area(
                                    "Generated Content",
                                    value=raw_text,
                                    height=200,
                                    key=f"saved_content_{idx}",
                                    label_visibility="collapsed"
                                )
                                
                                # Calculate reading time
                                read_info = compute_read_time(raw_text)
                                st.info(f"📖 Reading time: ~{read_info['estimated_read_time_minutes']} min ({read_info['word_count']} words)")
                        except Exception as e:
                            st.warning(f"⚠️ Could not load content: {e}")

else:
    # Show generator view
    
    # Handle generation
    if generate_btn:
        if not topic:
            st.error("❌ Please enter a topic to generate content")
        else:
            with st.spinner("🔄 Generating personalized content..."):
                prompt = f"""
Generate {num_items} high-quality study items for the topic: {topic}.

Target audience: {audience}
Study goal: {goal}
Include explanations: {include_explanations}

Format requirements:
- Number each item (1., 2., 3., etc.)
- For flashcards: use Q: ... and A: ... format with clear questions and concise answers
- For summaries: use clear paragraphs with numbered sections covering key concepts
- For comprehensive notes: provide detailed explanations with numbered points, examples, and important details

Provide comprehensive, accurate, and educational content focused on learning and understanding the topic.
Do NOT generate quiz questions with multiple choice options - this is for study materials only.
"""

                generated_text, err = generate_content(prompt)
                
                if err:
                    st.error(f"❌ Generation failed: {err}")
                else:
                    # Store in session state
                    st.session_state.generated_content = generated_text
                    st.session_state.content_metadata = {
                        'topic': topic,
                        'audience': audience,
                        'goal': goal,
                        'num_items': num_items
                    }
                    
                    # No question parsing needed - this is for study materials only
                    st.session_state.parsed_questions = []
                    
                    st.success("✅ Content generated successfully!")
                    st.rerun()

    # Display generated content
    if st.session_state.generated_content:
        st.markdown("---")
        st.header("📝 Generated Study Material")
        
        # Show metadata
        meta = st.session_state.content_metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📖 Topic", meta.get('topic', 'N/A'))
        with col2:
            st.metric("👥 Audience", meta.get('audience', 'N/A'))
        with col3:
            st.metric("🎯 Goal", meta.get('goal', 'N/A'))
        with col4:
            st.metric("📊 Items", meta.get('num_items', 0))
        
        st.markdown("---")
        
        # Show content
        st.subheader("📄 Content")
        st.text_area(
            "Generated Text",
            value=st.session_state.generated_content,
            height=300,
            key='content_display',
            label_visibility="collapsed"
        )
        
        # Show reading time
        read_info = compute_read_time(st.session_state.generated_content)
        st.info(f"📖 Estimated reading time: **~{read_info['estimated_read_time_minutes']} minutes** ({read_info['word_count']} words)")
        
        # SAVE SECTION - Always visible when content exists
        st.markdown("---")
        st.header("💾 Save Your Study Material")
        
        db, db_err = init_firestore()
        if db is None:
            st.warning(f"⚠️ Firestore not available: {db_err}")
            st.info("💡 To enable saving, configure Firebase credentials in your environment")
        else:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Topic:** {meta.get('topic', 'N/A')}")
                st.write(f"**Goal:** {meta.get('goal', 'N/A')}")
                st.write(f"**Collection:** `{COLLECTION_NAME}`")
            
            with col2:
                if st.button("💾 Save to Firestore", type="primary", use_container_width=True):
                    with st.spinner("Saving..."):
                        success, result = save_to_firestore(
                            db,
                            meta.get('topic', ''),
                            meta.get('audience', ''),
                            meta.get('goal', ''),
                            meta.get('num_items', 0),
                            st.session_state.generated_content,
                            st.session_state.parsed_questions
                        )
                        
                        if success:
                            st.success(f"✅ Successfully saved! (ID: {result})")
                            st.balloons()
                        else:
                            st.error(f"❌ Save failed: {result}")
    else:
        # Show welcome message
        st.info("👈 Enter a topic in the sidebar and click 'Generate Content' to get started!")
        
        st.markdown("---")
        st.subheader("✨ Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **📚 Generate Study Materials:**
            - Summaries (key concepts overview)
            - Flashcards (Q&A format)
            - Comprehensive Notes (detailed explanations)
            
            *For quiz questions, use the Quiz Generator!*
            """)
        
        with col2:
            st.markdown("""
            **💾 Save & Access:**
            - Automatic save to Firestore
            - Access anytime
            - Organized by topic
            - Reading time estimates
            """)