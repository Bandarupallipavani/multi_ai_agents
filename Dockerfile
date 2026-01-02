FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy only setup files first (for caching)
COPY setup.py pyproject.toml requirements.txt* ./

# Install dependencies
RUN pip install --no-cache-dir -e .

# Now copy rest of the code
COPY . .

EXPOSE 8501
EXPOSE 9999

CMD ["python", "app/main.py"]
