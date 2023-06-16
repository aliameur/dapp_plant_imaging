# Use an official Python runtime as a base image
FROM python:3.11

# Set the working directory in the Docker image
WORKDIR /flask_app

# Copy the current directory contents into the container at /flask_app
COPY . /flask_app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run main.py when the container launches
CMD ["python", "main.py"]