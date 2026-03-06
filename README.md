# Website Performance Dashboard (Streamlit)

This repository contains a Streamlit dashboard for website performance and channel portfolio analysis. The app reads CSVs in the project folder and renders interactive Plotly charts.

Files of interest
- `app.py`, `app2.py`, `app3.py` (Streamlit app files)
- `website_sessions.csv`, `website_pageviews.csv`, `orders.csv`, `products.csv`, `order_items.csv`, `order_item_refunds.csv` (data files)
- `.venv/` (local virtual environment, not committed)
- `requirements.txt` (Python dependencies generated from the venv)

Quick start (Windows PowerShell)

1. Open PowerShell and change to the project directory:

```powershell
Set-Location -Path 'A:\streamlit app'
```

2. Create and activate a virtual environment (skip if `.venv` already exists):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
# If activation is blocked, run:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

3. Install dependencies:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run the app (adjust filename if using `app.py`/`app2.py`/`app3.py`):

```powershell
streamlit run "A:\streamlit app\app3.py"
```

Making a Git repository and pushing to GitHub

1. Initialize a local git repo (I can do this for you, or run locally):

```powershell
git init
git add .
git commit -m "Initial commit: add Streamlit app and data"
```

2. Create a new GitHub repository (on github.com). Once created, link it and push:

```powershell
# replace <REMOTE_URL> with the GitHub repo URL (HTTPS or SSH)
git remote add origin <REMOTE_URL>
git branch -M main
git push -u origin main
```

Deployment options
- Streamlit Community Cloud: easiest for Streamlit apps. Connect the GitHub repo and pick the app file (`app3.py`).
- Heroku / Render / Railway: can host the app; you'll need a `Procfile` and the repo pushed to GitHub.

Notes
- Don't commit `.venv`. It's ignored via `.gitignore`.
- If your CSVs are large, consider storing them externally (S3) and loading them at runtime, or use Git LFS for large files.

If you want, I can:
- initialize the local git repo and make an initial commit now (I will not push to GitHub without your remote URL),
- or walk you step-by-step to create a GitHub repo and push from your machine.

Tell me which you'd like me to do next.
