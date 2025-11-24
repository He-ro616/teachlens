import os

db_path = 'teachlens-render/teachlens.db'
if os.path.exists(db_path):
    os.remove(db_path)
    print(f"Deleted {db_path}")
else:
    print(f"{db_path} not found, no deletion needed.")
