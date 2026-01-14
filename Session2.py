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
   "Regent College has campuses in Wembley, Kingsbury, Holborn, etc.—where exactly is yours located?", "How long will it take you to commute from your accommodation to the campus during rush hour?", "What is the nearest London Underground (Tube) station to your campus?", "Why did you choose to study in London despite the higher cost of living compared to other UK cities?", "What is your exact monthly budget for transport using the Transport for London (TfL) network?", "How much have you budgeted specifically for rent in London's private housing market?", "Have you identified the nearest police station and hospital to your planned accommodation?", "What is the 28-day rule regarding your maintenance funds in your bank account?", "If you have a gap in your education, how can you prove you were positively occupied during that time?", "What are the penalties if your attendance drops below the required threshold at Regent College?", "How will you handle the fast-paced lifestyle of London compared to your hometown?", "What is the maximum number of hours you can work per week during term time?", "Do you understand the difference between 'term time' and 'vacation time' for Master's students?", "Have you paid your tuition deposit, and is it refundable if your visa is rejected?", "Who is your financial sponsor, and have they provided a letter of consent?", "What documents will you need to present to the Border Force officer upon landing at Heathrow/Gatwick?", "How will you transfer money from your home country to the UK for your daily expenses?", "Do you have any family members or close friends currently living in London?", "What is the cost of the Immigration Health Surcharge (IHS) for your course duration?", "If you lose your BRP (Biometric Residence Permit), what is the first thing you must do?", "Have you checked the crime rate in the area where you plan to live in London?", "What specific clothing have you packed for the London winter?", "Can you explain why you are applying for a visa now and not six months ago?", "What will you do during the summer period of your course?", "If your primary accommodation falls through, do you have a temporary backup plan?"
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
