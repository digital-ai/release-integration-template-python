# Use the Python image as the base
FROM python:alpine3.17

# Prevent Python from writing bytecode files and run in unbuffered mode
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the source code into the container
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the entrypoint command
CMD ["python", "-m", "digitalai.release.integration.wrapper"]