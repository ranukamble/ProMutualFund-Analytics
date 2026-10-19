import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

# 1. Directories to ensure
data_dir = os.path.join(BASE_DIR, "data")
tests_dir = os.path.join(BASE_DIR, "tests")
scripts_dir = os.path.join(BASE_DIR, "scripts")
patches_dir = os.path.join(scripts_dir, "patches")

ensure_dir(data_dir)
ensure_dir(tests_dir)
ensure_dir(scripts_dir)
ensure_dir(patches_dir)

# 2. File movements mapping
moves = [
    # Data files to data/
    ("active_funds.json", data_dir),
    ("all_funds_powerbi.csv", data_dir),
    ("mutual_funds.db", data_dir),
    ("saved_portfolio.json", data_dir),
    ("saved_portfolios.json", data_dir),
    ("scheme_codes.json", data_dir),

    # Test files to tests/
    ("test_api.py", tests_dir),
    ("test_cohere.py", tests_dir),
    ("test_common_dates.py", tests_dir),
    ("test_dates.py", tests_dir),
    ("test_mfapi.py", tests_dir),

    # Maintenance & utility scripts to scripts/
    ("add_ui.py", scripts_dir),
    ("check_syntax.py", scripts_dir),
    ("demo.py", scripts_dir),
    ("fetch_all_40k_funds.py", scripts_dir),
    ("fix.py", scripts_dir),
    ("parse_groww.py", scripts_dir),
    ("refactor.py", scripts_dir),
    ("search_mf.py", scripts_dir),
    ("update_active_funds.py", scripts_dir),
    ("portfolio.html", scripts_dir),

    # One-off UI/Logic patches to scripts/patches/
    ("patch_analysis_ui.py", patches_dir),
    ("patch_chart_tooltips.py", patches_dir),
    ("patch_donut_legend.py", patches_dir),
    ("patch_generate_ui.py", patches_dir),
    ("patch_js.py", patches_dir),
    ("patch_light_overview.py", patches_dir),
    ("patch_light_pg.py", patches_dir),
    ("patch_light_text.py", patches_dir),
    ("patch_logo.py", patches_dir),
    ("patch_projection.py", patches_dir),
    ("patch_smooth.py", patches_dir),
    ("patch_theme.py", patches_dir),
    ("patch_ui.py", patches_dir),
]

moved_count = 0
for filename, target_dir in moves:
    src = os.path.join(BASE_DIR, filename)
    dst = os.path.join(target_dir, filename)
    if os.path.exists(src):
        # If destination file already exists and is not the same, remove it or overwrite
        if os.path.exists(dst) and src != dst:
            os.remove(dst)
        shutil.move(src, dst)
        moved_count += 1
        print(f"Moved: {filename} -> {os.path.relpath(target_dir, BASE_DIR)}")

print(f"\nDone! Successfully moved {moved_count} files into clean directory structure.")
