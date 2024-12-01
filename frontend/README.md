# frontend

## Project setup
```
npm install
```

### Compiles and hot-reloads for development
```
npm run serve
```

### Compiles and minifies for production
```
npm run build
```

### Lints and fixes files
```
npm run lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## Uninstallation

To completely remove the application:

1. Stop all running services:
   - On Unix: `pkill -f 'uvicorn|streamlit'`
   - On Windows: Use Ctrl+C in the terminal running the setup script

2. Remove the virtual environment and generated files:
   ```bash
   # Unix/macOS
   rm -rf .venv
   rm backend/backend.log frontend/frontend.log
   rm -rf frontend/.streamlit
   ```
   ```powershell
   # Windows
   Remove-Item -Recurse -Force .venv
   Remove-Item backend/backend.log, frontend/frontend.log
   Remove-Item -Recurse -Force frontend/.streamlit
   ```

3. If you want to remove FFmpeg (optional):
   - Ubuntu/Debian: `sudo apt-get remove ffmpeg`
   - macOS: `brew uninstall ffmpeg`
   - Windows: Uninstall through Windows Settings or Control Panel

4. Delete the project directory:
   ```bash
   # Unix/macOS
   cd ..
   rm -rf video-transcription-app
   ```
   ```powershell
   # Windows
   cd ..
   Remove-Item -Recurse -Force video-transcription-app
   ```

To stop the application:
- On Unix: `pkill -f 'uvicorn|streamlit'`
- On Windows: Use Ctrl+C in the terminal running the setup script
