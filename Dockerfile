FROM python:3.9

# Install system dependencies
RUN apt-get update && apt-get install -y \
    poppler-utils \
    tesseract-ocr \
    libtesseract-dev \
    libgl1-mesa-glx \
    libheif-dev \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

WORKDIR $HOME/app

# Copy the requirements file into the container
COPY --chown=user requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --user --no-cache-dir -r requirements.txt \
    && pip install --user --no-cache-dir pyheif

# Copy the rest of the working directory contents into the container
COPY --chown=user . .

# Run app.py when the container launches
CMD ["chainlit", "run", "app2.py", "--port", "7860"]