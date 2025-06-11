FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    wget \
    ca-certificates \
    ffmpeg \
    pkg-config \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-fra \
    tesseract-ocr-spa \
    tesseract-ocr-deu \
    libmagic-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgl1-mesa-glx \
    libfontconfig1-dev \
    libcairo2-dev \
    libglib2.0-dev \
    libjpeg62-turbo-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    liblcms2-dev \
    libcurl4-openssl-dev \
    libboost-dev \
    && rm -rf /var/lib/apt/lists/*

RUN cd /tmp && \
    wget https://poppler.freedesktop.org/poppler-24.08.0.tar.xz && \
    tar -xf poppler-24.08.0.tar.xz && \
    cd poppler-24.08.0 && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release \
          -DCMAKE_INSTALL_PREFIX=/usr/local \
          -DENABLE_UNSTABLE_API_ABI_HEADERS=ON \
          -DENABLE_NSS3=OFF \
          -DENABLE_GPGME=OFF \
          -DENABLE_QT5=OFF \
          -DENABLE_QT6=OFF \
          -DENABLE_GLIB=OFF \
          -DENABLE_GOBJECT_INTROSPECTION=OFF \
          -DENABLE_CPP=ON \
          -DENABLE_UTILS=ON \
          -DBUILD_SHARED_LIBS=ON \
          -DENABLE_BOOST=OFF \
          .. && \
    make -j$(nproc) && \
    make install && \
    ldconfig && \
    cd / && \
    rm -rf /tmp/poppler-24.08.0*

# Find and set correct tessdata path dynamically
RUN TESSDATA_PATH=$(find /usr/share -name "tessdata" -type d 2>/dev/null | head -1) && \
    echo "Found tessdata at: $TESSDATA_PATH" && \
    echo "TESSDATA_PREFIX=$TESSDATA_PATH" >> /etc/environment

ENV TESSERACT_CMD="/usr/bin/tesseract" \
    UNSTRUCTURED_HOME="/app/.unstructured_cache" \
    PATH="/usr/local/bin:/usr/bin:${PATH}" \
    PYTHONPATH="/app/src:${PYTHONPATH}" \
    LD_LIBRARY_PATH="/usr/local/lib:${LD_LIBRARY_PATH}" \
    PKG_CONFIG_PATH="/usr/local/lib/pkgconfig:${PKG_CONFIG_PATH}"

COPY requirements.txt .

RUN pip install --timeout 1800 -vvv -r requirements.txt \
    && pip install --timeout 1800 -vvv unstructured \
    && pip install --timeout 1800 -vvv pdfminer.six \
    && pip install --timeout 1800 -vvv pi_heif \
    && pip install --timeout 1800 -vvv unstructured_inference \
    && pip install --timeout 1800 -vvv pdf2image \
    && pip install --timeout 1800 -vvv python-dotenv \
    && pip install --timeout 1800 -vvv openai \
    && pip install --timeout 1800 -vvv chromadb \
    && pip install --timeout 1800 -vvv flask_cors \
    && pip install unstructured[pdf,ocr] \
    && pip install hf_xet 

RUN mkdir -p /app/.unstructured_cache && \
    chmod 777 /app/.unstructured_cache && \
    mkdir -p /app/uploads && \
    chmod 777 /app/uploads

RUN mkdir -p /app/temp && \
    chmod 777 /app/temp

RUN mkdir -p /app/drafts && \
    chmod 777 /app/drafts

RUN mkdir -p /app/finalized && \
    chmod 777 /app/finalized

COPY src/ ./src/

RUN pdftoppm -v && pdfinfo -v && tesseract --version && echo "Poppler and Tesseract installed successfully"

CMD ["/bin/bash", "-c", "source /etc/environment && flask --app src.server run --port=5000 --host=0.0.0.0"]