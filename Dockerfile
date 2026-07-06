# Use the Python image as the base
FROM python:alpine3.21

# Prevent Python from writing bytecode files and run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory (created automatically) and make it writable
WORKDIR /app
RUN chmod 777 /app

# Copy the dependency list first and install it, so Docker caches the (slow)
# pip layer and only re-runs it when requirements.txt changes — not on every
# edit to the task code below.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the task code. .dockerignore keeps this to src/ only, so the image
# ships just the code it runs.
COPY src/ ./src/

# Set the entrypoint command
CMD ["python", "-m", "digitalai.release.integration.wrapper"]