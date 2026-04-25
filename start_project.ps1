Write-Host "Checking and installing dependencies..."
.\venv_gpu\Scripts\pip.exe install -r requirements.txt

Write-Host "Starting FastAPI Backend..."
Start-Process -FilePath ".\venv_gpu\Scripts\python.exe" -ArgumentList "-m", "uvicorn", "src.api.main:app", "--reload", "--port", "8000"

Write-Host "Starting Streamlit Dashboard..."
Start-Process -FilePath ".\venv_gpu\Scripts\python.exe" -ArgumentList "-m", "streamlit", "run", "src/dashboard/app.py"

Write-Host "Both services have been started in new windows!"
