path = r"C:\Users\user\Documents\cap_kt_app\app.py"

with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# Ganti tab dengan 4 spasi
fixed = [line.replace("\t", "    ") for line in lines]

with open(path, "w", encoding="utf-8") as f:
    f.writelines(fixed)

print("Selesai! Semua tab sudah diganti 4 spasi.")
