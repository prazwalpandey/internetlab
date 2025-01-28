# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose ports for FastAPI and Streamlit
EXPOSE 8000 8501

# Command to run both FastAPI and Streamlit
CMD streamlit run frontend/app.py --server.port 8501 & uvicorn backend.main:app --host 0.0.0.0 --port 8000

