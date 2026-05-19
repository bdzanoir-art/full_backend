"""
migrate_all.py  —  Run migrations for ALL backends with one command:
    python migrate_all.py

Runs `migrate` in each backend directory so all databases are up to date.
"""

import subprocess
import sys
import os

BACKENDS = [
    {"name": "ESI-GM",              "dir": "backend-esi_gm",               "settings": "aproject.settings"},
    {"name": "Inventory",           "dir": "backend-inventory",            "settings": "config.settings"},
    {"name": "Admin Dashboard",     "dir": "backend_admin_dashboard",      "settings": "config.settings"},
    {"name": "QR Stock Scanner",    "dir": "backend_QR_Stock_Scanner",     "settings": "config.settings"},
    {"name": "Browse",              "dir": "backend_browse",               "settings": "core.settings"},
    {"name": "Login",               "dir": "backend_login",                "settings": "core.settings"},
    {"name": "Materials Transfer",  "dir": "backend_materials_transfert",  "settings": "config.settings"},
    {"name": "My Requests",         "dir": "backend_my_request",           "settings": "config.settings"},
]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
python   = sys.executable


def run_migrate(backend):
    cwd = os.path.join(BASE_DIR, backend["dir"])
    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = backend["settings"]

    print(f"\n{'='*55}")
    print(f"  Migrating: {backend['name']}")
    print(f"{'='*55}")

    result = subprocess.run(
        [python, "manage.py", "migrate"],
        cwd=cwd,
        env=env,
    )
    if result.returncode != 0:
        print(f"  [!] Migration FAILED for {backend['name']}")
    else:
        print(f"  [✓] Migration OK for {backend['name']}")


if __name__ == "__main__":
    print("\n  ESI-GM — Running migrations for all backends\n")
    for b in BACKENDS:
        run_migrate(b)
    print("\n  Done.\n")
