FROM python:3.9-slim

# Install system dependencies for LightGBM and other potential packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that Streamlit will use
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "main.py"]
