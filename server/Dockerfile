# ───────────────────────── base image ─────────────────────────
FROM python:3.13.3-slim

# Set the working directory inside the container
WORKDIR /app

# ─────────────────── install Python dependencies ──────────────
# Copy only the requirements file first so Docker can cache this
# layer when code changes but dependencies do not.
COPY requirements.txt ./

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# ─────────────────────── copy application ─────────────────────
COPY . .

# Expose FastAPI’s default port
EXPOSE 8000

# ─────────────────────────── run app ──────────────────────────
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
