# Use an official lightweight Python runtime
FROM python:3.11-slim

# Set system environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for Python packages (e.g., yaml/gcc additions if required later)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies cleanly without caching installation files
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project codebase into the container
COPY . .

# Run the simulation engine by default when the container boots
CMD ["python", "main.py"]