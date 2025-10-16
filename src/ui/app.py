import streamlit as st
import requests
import json
import time

# --- 1. CONFIGURATION ---
API_URL = "http://127.0.0.1:8000/chat"
st.set_page_config(page_title="Contextual Interview Coach", page_icon="🤖")

# --- 2. APP UI ---
st.title("🤖 Contextual Interview Coach")
st.markdown("Upload your resume and paste a job description to start a realistic, AI-powered interview.")

# Initialize chat history in session state if it doesn't exist
if "history" not in st.session_state:
    st.session_state.history = []

# Sidebar for inputs
with st.sidebar:
    st.header("Your Documents")
    cv_file = st.file_uploader("Upload your Resume/CV (PDF)", type=["pdf"])
    jd_text = st.text_area("Paste the Job Description Here")

# --- 3. DISPLAY CHAT HISTORY ---
for message in st.session_state.history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 4. HANDLE USER INPUT AND API CALL ---
prompt = st.chat_input("Your answer...")
if prompt:
    # Add user message to history and display it
    st.session_state.history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Check if all inputs are provided
    if cv_file is None or not jd_text.strip():
        with st.chat_message("assistant"):
            st.warning("Please upload your resume and paste the job description in the sidebar to start.")
    else:
        # Prepare data for the API request
        files = {'cv_file': (cv_file.name, cv_file.getvalue(), cv_file.type)}
        data = {
            'jd_text': jd_text,
            'history_str': json.dumps(st.session_state.history) # Send history as a JSON string
        }

        # Show a spinner while waiting for the API response
        with st.spinner("Assistant is thinking..."):
            try:
                response = requests.post(API_URL, files=files, data=data)
                response.raise_for_status() # Raise an exception for bad status codes
                
                ai_response = response.json()["response"]
                time.sleep(1) 

                # Add assistant response to history and display it
                st.session_state.history.append({"role": "assistant", "content": ai_response})
                with st.chat_message("assistant"):
                    st.markdown(ai_response)

            except requests.exceptions.RequestException as e:
                st.error(f"Failed to connect to the backend API. Please make sure the server is running. Error: {e}")