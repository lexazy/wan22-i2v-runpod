# Image de base NVIDIA CUDA
FROM nvidia/cuda:12.1.0-cudnn8-devel-ubuntu22.04

# Variables d'environnement
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    git \
    wget \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Créer le répertoire de travail
WORKDIR /app

# Clone le repo Wan 2.2
RUN git clone https://github.com/Wan-Video/Wan2.2.git /app/Wan2.2

# Installation des dépendances Python essentielles
WORKDIR /app/Wan2.2
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
RUN pip3 install --no-cache-dir \
    diffusers \
    transformers \
    accelerate \
    pillow \
    numpy \
    opencv-python-headless \
    imageio \
    einops \
    omegaconf \
    safetensors \
    "huggingface_hub[cli]"

# ✅ TÉLÉCHARGER LE MODÈLE LÉGER TI2V-5B (5GB) pendant le build
RUN mkdir -p /app/models && \
    python3 -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='Wan-AI/Wan2.2-TI2V-5B', local_dir='/app/models/Wan2.2-TI2V-5B', local_dir_use_symlinks=False)"

# Copier le handler
COPY handler.py /app/handler.py

# Installer RunPod SDK
RUN pip3 install --no-cache-dir runpod

# Port
EXPOSE 8000

# Démarrage
CMD ["python3", "/app/handler.py"]
