FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    libegl1 \
    libgles2 \
    libglx-mesa0 \
    libopengl0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libusb-1.0-0 \
    ffmpeg \
    libopus0 \
    libvpx7 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY src ./src
COPY services ./services
COPY utils ./utils
COPY models ./models

EXPOSE 8501

ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
