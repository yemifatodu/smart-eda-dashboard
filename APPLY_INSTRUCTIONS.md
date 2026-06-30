# How to apply these fixes to your repo

1. Copy these files into your repo at the SAME paths, overwriting what's there:
   - app.py
   - api.py
   - requirements.txt   (just adds `requests`)
   - .gitignore          (adds data/users.json, .env)
   - pages/auth.py
   - pages/dashboard.py
   - pages/comparison.py
   - pages/storytelling.py
   - pages/anomaly.py
   - pages/undo_redo.py
   - pages/collaboration.py
   - pages/data_sources.py
   - utils/usage_tracker.py   (new file)

2. Delete these now-redundant files from your repo:
   - app.py.backup
   - pages/07_dashboard.py
   - pages/08_comparison.py
   - pages/09_storytelling.py
   - pages/10_auth.py
   - pages/12_anomaly.py
   - pages/13_data_sources.py
   - pages/14_undo_redo.py
   - pages/15_collaboration.py
   (their content now lives in the canonical pages/*.py files above)

3. If data/users.json already exists and was ever committed, remove it from
   git history (not just gitignore it going forward):
   git rm --cached data/users.json   (if tracked)

4. Run `pip install -r requirements.txt` again to pick up `requests`.

5. First run will print a generated admin password to your terminal/server
   logs once — save it, then change it via "Change Password" in the app.
   Don't reuse admin123.

## What's intentionally still a placeholder
- utils/usage_tracker.py tracks free-tier counts but upgrade_to_pro() does
  NOT verify payment — that's the Stripe work you're doing last. Don't wire
  any "Upgrade" button to call it directly until Stripe is in place.
- api.py's /predict endpoint now returns a clear 501 "not implemented"
  instead of silently echoing the request back.
