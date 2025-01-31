# Use the official Python image
FROM python:3.9

# Set the working directory inside the container
WORKDIR /app

# Copy all project files into the container
COPY . .

# Move into the app directory
WORKDIR /app/app

# Install dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose Streamlit port
EXPOSE 8501

# Run the Streamlit app from the correct directory
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
