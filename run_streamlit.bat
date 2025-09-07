@echo off
set STREAMLIT_SERVER_HEADLESS=false
set STREAMLIT_SERVER_PORT=5003
set STREAMLIT_SERVER_ENABLE_CORS=false
set STREAMLIT_SERVER_ENABLE_XSRF=false
set BROWSER=chrome

start "" http://localhost:5003
streamlit run main.py --server.port=5003 --server.headless=false --server.enableCORS=false --server.enableXsrfProtection=false
