import os
import glob
import re

base = r"c:\Users\j\OneDrive\Desktop\full_backend\apps"

apps = ["esi_gm", "inventory", "browse", "login_app", "my_request", "scanner", "transfers"]

for app in apps:
    app_dir = os.path.join(base, app)
    
    # 1. Clear models.py and admin.py
    for fname in ["models.py", "admin.py"]:
        fpath = os.path.join(app_dir, fname)
        if os.path.exists(fpath):
            with open(fpath, "w", encoding="utf-8") as f:
                f.write("# Migrated to apps.core\n")
    
    # 2. Update serializers.py and views.py to import from apps.core.models
    for fname in ["serializers.py", "views.py", "authentication.py"]:
        fpath = os.path.join(app_dir, fname)
        if not os.path.exists(fpath):
            continue
            
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Replace `from .models import ...` with `from apps.core.models import ...`
        content = re.sub(r'from\s+\.models\s+import', 'from apps.core.models import', content)
        content = re.sub(r'from\s+\.\s+import\s+models', 'from apps.core import models', content)
        
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)

print("Refactored imports.")
