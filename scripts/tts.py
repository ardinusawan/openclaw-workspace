import pyttsx3
import sys

engine = pyttsx3.init()
text = " ".join(sys.argv[1:])
engine.save_to_file(text, "output.wav")
engine.runAndWait()
print(f"Saved: {text} -> output.wav")
