# FROM python:3.11-slim

# WORKDIR /app

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     postgresql-client \
#     && rm -rf /var/lib/apt/lists/*

# # Install Poetry
# RUN pip install poetry

# # Copy project files and install dependencies
# COPY pyproject.toml poetry.lock* ./

# RUN poetry install --no-root --no-interaction --no-ansi

# # Copy application code
# COPY app/ ./app/
# COPY .env .

# # Expose port
# EXPOSE 8033

# # Command to run the application
# # CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8033"]
# CMD ["poetry", "run", "uvicorn", "main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "8033"]