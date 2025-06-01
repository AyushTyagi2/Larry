# tasks/voice/speech.py
import pyttsx3
import speech_recognition as sr
import threading
import queue

# Global variables
speech_engine = None
voice_queue = queue.Queue()
listening_active = False

def initialize_speech_engine():
    global speech_engine
    if speech_engine is None:
        speech_engine = pyttsx3.init()
        # Optional: Configure voice settings
        # voices = speech_engine.getProperty('voices')
        # speech_engine.setProperty('voice', voices[1].id)  # Index 1 is usually a female voice
        speech_engine.setProperty('rate', 170)  # Speech rate
    return speech_engine

def speak_text(text):
    """Convert text to speech"""
    engine = initialize_speech_engine()
    print(f"🔊 Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def voice_worker():
    """Process voice commands from queue"""
    while True:
        text = voice_queue.get()
        if text == "EXIT":
            break
        speak_text(text)
        voice_queue.task_done()

def start_voice_thread():
    """Start the voice processing thread"""
    voice_thread = threading.Thread(target=voice_worker, daemon=True)
    voice_thread.start()
    return voice_thread

def queue_speech(text):
    """Add text to speech queue to avoid blocking"""
    voice_queue.put(text)

def listen_for_command():
    """Listen for voice command and convert to text"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(source, timeout=5)
            
        print("Processing speech...")
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.WaitTimeoutError:
        print("No speech detected")
        return None
    except sr.UnknownValueError:
        print("Could not understand audio")
        return None
    except sr.RequestError as e:
        print(f"Speech recognition service error: {e}")
        return None
    except Exception as e:
        print(f"Error in speech recognition: {e}")
        return None

def toggle_voice_listening():
    """Toggle voice command listening on/off"""
    global listening_active
    listening_active = not listening_active
    status = "enabled" if listening_active else "disabled"
    print(f"Voice commands {status}")
    return listening_active