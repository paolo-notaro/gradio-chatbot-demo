# Use the official Python image as a base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Create and start virtual environment
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate"

# Install dependencies
RUN pip install -r requirements.txt

# Optional: Add step to run tests here (PyTest, Django test suites, etc.)

# Zip artifact for deployment
RUN apt-get update && apt-get install -y zip
RUN zip -r release.zip ./*

# Define a volume
VOLUME /app/venv

# Expose any ports the app is expecting
# (e.g. if your application exposes port 8080, then you should use EXPOSE 8080 here)
EXPOSE 8000

# Command to run the application
CMD ["python", "-m", "src.frontend.app", ">", "app.log"]
