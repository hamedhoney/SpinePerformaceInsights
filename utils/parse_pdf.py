import fitz 

pdf_path = "data/dissertation.pdf"
doc = fitz.open(pdf_path)

full_text = ""
for page in doc:
    full_text += page.get_text()

chapters = full_text.split("Chapter")

with open("data/dissertation.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
