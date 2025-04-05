# Development Dockerfile
FROM ubuntu
SHELL ["/bin/bash", "-c"]

# Create user with host's UID/GID to avoid permission issues
RUN groupadd --gid 1024 shared
RUN useradd -m --group sudo,shared sat && passwd -d sat

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    sudo git nano curl gnupg \
    build-essential python3 python3-dev python3-venv \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

USER sat
WORKDIR /home/sat

# Setup Python virtual environment
ENV VIRTUAL_ENV=/home/sat/.venv/sat
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install Python dependencies
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Configure work directory with proper permissions
WORKDIR /home/sat/work
RUN sudo chown :1024 . && sudo chmod 775 . && sudo chmod g+s .

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]