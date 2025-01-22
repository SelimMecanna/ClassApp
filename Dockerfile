FROM python:3.11-slim

# Set environment variables to suppress interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Install curl using apt-get
RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . ./

# Install required Python packages
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 5000

# Command to run the application
CMD ["uvicorn", "classify_image:app", "--host", "0.0.0.0", "--port", "5000"]