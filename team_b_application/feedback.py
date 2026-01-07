import pyttsx3
import threading

def speak_worker(text):
    """
    Worker function that creates a fresh engine instance for every speech command.
    This prevents the 'run loop already started' error.
    """
    try:
        # Initialize a NEW engine instance just for this specific message
        engine = pyttsx3.init()
        engine.setProperty('rate', 150) # Optional: Adjust speed
        engine.say(text)
        engine.runAndWait()
    except RuntimeError:
        # If the engine is somehow still busy, just ignore this specific error to keep app running
        pass

def speak(text):
    """
    Call this function to say something without blocking the main program
    """
    thread = threading.Thread(target=speak_worker, args=(text,))
    thread.start()