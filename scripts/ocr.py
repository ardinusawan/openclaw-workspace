import sys
import pytesseract
from PIL import Image

image_path = sys.argv[1]
image = Image.open(image_path)

# OCR with Indonesian language
text = pytesseract.image_to_string(image, lang='ind')

print(text)
