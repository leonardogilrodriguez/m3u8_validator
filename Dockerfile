# Stage 1: Build dependencies and install Python packages
FROM python:3.10-alpine3.22 as builder

# Python environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install minimal build dependencies
# Only include gcc and musl-dev if you have packages that require compilation
RUN apk add --no-cache \
    gcc \
    musl-dev \
    python3-dev

# Copy requirements and install Python dependencies to a local user directory
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final image for running the application
FROM python:3.10-alpine3.22

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Copy only the necessary files from the builder stage
COPY --from=builder /root/.local /root/.local
COPY . .

# Add local user bin directory to PATH
ENV PATH=/root/.local/bin:$PATH

# Install curl for possible health checks or debugging
RUN apk add --no-cache curl

# Expose the application port
EXPOSE 5665

# Start the Gunicorn server with 4 workers and 2 threads per worker
CMD ["gunicorn", "-w", "4", "-k", "gthread", "--threads", "2", "--timeout", "180", "-b", "0.0.0.0:5665", "server:app"]