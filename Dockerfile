# 1. Use the official lightweight Python 3.11 image
FROM python:3.11-slim

# 2. Prevent Python from buffering stdout/stderr and writing byte-compiled files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 3. Create a non-root user for security
RUN useradd -m appuser

# 4. Set the working directory
WORKDIR /app

# 5. Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the application code
COPY . .

# 7. Change ownership of the app directory to the non-root user
RUN chown -R appuser:appuser /app

# 8. Switch to the non-root user
USER appuser

# 9. Expose the port (must match the port in the Uvicorn command)
EXPOSE 8080

# 10. Run the application, binding to 0.0.0.0 for container networking
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]