path = r"C:\Users\user\Documents\cap_kt_app\app.py"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# ganti non-breaking space (U+00A0) dengan spasi biasa
content = content.replace("\u00A0", " ")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Selesai, semua karakter U+00A0 sudah diganti spasi biasa.")
