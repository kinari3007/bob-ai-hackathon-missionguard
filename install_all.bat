@echo off
".venv\Scripts\pip.exe" install fastapi==0.115.12 uvicorn[standard]==0.34.2 httpx==0.28.2 streamlit==1.45.1 requests==2.32.3 --quiet
".venv\Scripts\python.exe" check_deps.py
echo Done.
