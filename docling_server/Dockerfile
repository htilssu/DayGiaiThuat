FROM python:3.12-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir docling
RUN docling-tools models download
RUN pip install --no-cache-dir runpod
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your handler file
COPY main.py .
COPY . .

# Start the container
CMD ["python3", "-u", "main.py"]