FROM debian:bullseye-slim

WORKDIR /app

# Install Python and build dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt aiofiles

# Copy the rest of the application
COPY . .

# Create output directory and ensure proper permissions
RUN mkdir -p output && chmod 755 output

# Expose the port
EXPOSE 5050

# Command to run the application
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5050"] 