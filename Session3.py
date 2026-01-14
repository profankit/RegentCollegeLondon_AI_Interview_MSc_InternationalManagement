import streamlit as st
import streamlit.components.v1 as components
import os
import time

# --- CONFIGURATION ---
# We now fetch the password from Streamlit Secrets instead of hardcoding it
try:
    ADMIN_PASSWORD = st.secrets["admin"]
except KeyError:
    # Fallback for local testing if secrets.toml isn't set up yet
    # You can remove this fallback before deploying if you want strict security
    ADMIN_PASSWORD = "Delta" 
except FileNotFoundError:
    ADMIN_PASSWORD = "Delta"

QUESTIONS = [
"What is the exact job title you are targeting immediately after graduation?", "Name three companies in your home country that specifically hire MBA graduates from the UK.", "How many years will it take you to earn back the money spent on this degree?", "Why do you need a British MBA specifically, rather than an MBA from the USA or Australia?", "What is the average salary for a Business Manager in your home country right now?", "How much of a salary increment do you expect after completing this MBA?", "How does this MBA specifically help you if you want to become an entrepreneur?", "Which specific management skill do you currently lack that this course will teach you?", "Have you looked at the alumni profiles of Regent College London to see where they are working?", "If you do not get a job immediately upon returning home, what is your Plan B?", "Why not just gain work experience for two more years instead of paying for an MBA?", "How will you explain the value of a UK degree to an employer in your home country?", "What is the current economic growth rate of your home country and how does it affect your career?", "Do you plan to utilize the Graduate Route (Post-Study Work) visa?", "If you plan to stay in the UK for the Graduate Route, how will you support yourself financially while job hunting?", "What specific industry sector (e.g., Retail, Tech, Manufacturing) are you targeting?", "How does the 'Global' nature of London business help your career back home?", "Will you look for part-time work in London that is related to your MBA?", "How will you balance a part-time job with your intensive MBA studies?", "What is the difference between a 'Manager' and a 'Leader' in your opinion?", "Have you ever been refused a visa for any other country?", "Why is this the right time in your career to take a break and study?", "What is the most significant business challenge your home country faces right now?", "How will networking in London help your family business (if applicable)?", "What makes you a better candidate for this MBA than other applicants?"   
]

# --- PAGE SETUP ---
st.set_page_config(page_title="Professor Ankit's AI Online Interview Preperation", page_icon="🤖")

# --- LOGIN SYSTEM (FIXED INDENTATION) ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.write("Welcome to")
    st.title("Regent College Longon AI Based Interview System")
    st.title("🔒 Restricted Access")
    st.write("Please enter the password to begin the interview.")
    
    # 1. Input field
    password_input = st.text_input("Enter Password:", type="password")
    
    # 2. Login Button
    if st.button("Login 🔐"):
        if password_input == ADMIN_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()  # Reload the app to show the interview content
        else:
            st.error("❌ Incorrect Password. Please try again.")
            
    st.stop()  # Stops the rest of the app from loading until logged in

# --- HELPER FUNCTIONS ---
def native_speak_button(text):
    """Creates a button to read the question using phone's voice."""
    safe_text = text.replace("'", "").replace('"', "")
    html_code = f"""
    <div style="display: flex; justify-content: center; margin-bottom: 20px;">
        <button onclick="
            var msg = new SpeechSynthesisUtterance('{safe_text}');
            msg.lang = 'en-US';
            window.speechSynthesis.cancel();
            window.speechSynthesis.speak(msg);
        " style="padding: 10px 20px; font-size: 18px; border-radius: 8px; border: none; background-color: #ff4b4b; color: white; cursor: pointer;">
            🔊 Tap to Hear Question
        </button>
    </div>
    """
    components.html(html_code, height=80)

def mark_download_clicked(q_index):
    """Callback to record that the user clicked download for the current question."""
    st.session_state[f"saved_q{q_index}"] = True

# --- MAIN APP ---
st.title("Professor Ankit's")
st.title("AI Online Interview Preperation")
st.write("")
st.write("This app will help you to practice recent CAS interview questions asked from the students. Please ensure that you may have working speakers/headset and a microphone. Please CLICK on the Play button to listen to the question, then record your answer by clicking on the microphone button.")
st.write("Once the answer is recorded then move to next question")

if 'q_index' not in st.session_state:
    st.session_state.q_index = 0

# Check if interview is finished
if st.session_state.q_index < len(QUESTIONS):
    
    # 1. GET QUESTION
    current_q = QUESTIONS[st.session_state.q_index]
    st.subheader(f"Question {st.session_state.q_index + 1}")
    
    # 2. SPEAK QUESTION
    st.info(f"🗣️ **AI Asks:** {current_q}")
    native_speak_button(current_q)

    # 3. RECORD / UPLOAD VIDEO
    st.write("👇 **Tap on the icon, select 'Take Video' to record your video.**")
    
    video_file = st.file_uploader(
        f"Upload Video for Q{st.session_state.q_index + 1}", 
        type=['mp4', 'mov', 'avi'], 
        accept_multiple_files=False
    )

    if video_file is not None:
        st.success("✅ Video Recording Complete!")
        
        # Show a preview of the video
        st.video(video_file)
        
        # --- LOGIC TO HANDLE DELAY ---
        
        # Create unique keys for the current question index
        save_key = f"saved_q{st.session_state.q_index}"
        timer_key = f"timer_done_q{st.session_state.q_index}"
        
        # Initialize session state for this specific question if not present
        if save_key not in st.session_state:
            st.session_state[save_key] = False
        if timer_key not in st.session_state:
            st.session_state[timer_key] = False

        st.warning("⚠️ Step 1: Please click on the button below to save the video to your device.")
        
        # 4. DOWNLOAD BUTTON
        st.download_button(
            label="⬇️ Save Video (Required)",
            data=video_file,
            file_name=f"Student_Answer_Q{st.session_state.q_index + 1}.mp4",
            mime="video/mp4",
            on_click=mark_download_clicked,
            args=(st.session_state.q_index,)
        )

        # 5. COUNTDOWN & SUBMIT BUTTON LOGIC
        # This block executes only AFTER the download button is clicked
        if st.session_state[save_key]:
            
            placeholder = st.empty()

            # If timer hasn't finished yet, show the countdown
            if not st.session_state[timer_key]:
                for i in range(5, 0, -1):
                    placeholder.info(f"⏳ Verifying save... Next button appears in {i} seconds")
                    time.sleep(1)
                
                # Mark timer as done and rerun to refresh the page
                st.session_state[timer_key] = True
                placeholder.empty()
                st.rerun()

            # If timer is finished, show the Next button
            if st.session_state[timer_key]:
                st.success("Video saved successfully!")
                st.info("Submit all the videos to WhatsApp for evaluation after the interview session completes.")
                
                if st.button("Submit & Next Question ➡️"):
                    st.session_state.q_index += 1
                    st.rerun()

else:
    st.balloons()
    st.success("🎉 Interview Completed! Thank you.")
    
    if st.button("Start New Interview"):
        st.session_state.q_index = 0
        st.session_state.authenticated = False
        
        # Clear specific session state keys
        keys_to_clear = [k for k in st.session_state.keys() if k.startswith("saved_q") or k.startswith("timer_done_q")]
        for key in keys_to_clear:
            del st.session_state[key]
            
        st.rerun()
