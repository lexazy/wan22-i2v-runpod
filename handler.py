import runpod
import json
import subprocess
import base64
import os
from pathlib import Path

WAN22_DIR = "/app/Wan2.2"
MODEL_DIR = "/app/Wan2.2/models/Wan2.2-I2V-A14B"
OUTPUT_DIR = "/app/Wan2.2/outputs"

def generate_video(image_path, prompt, duration=5):
    """Génère une vidéo avec Wan 2.2 I2V"""
    
    # Créer le dossier de sortie
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Commande de génération
    cmd = [
        "python3",
        f"{WAN22_DIR}/generate.py",
        "--task", "i2v-A14B",
        "--size", "1280*720",
        "--ckpt_dir", MODEL_DIR,
        "--image", image_path,
        "--prompt", prompt,
        "--output_dir", OUTPUT_DIR,
        "--convert_model_dtype",
        "--offload_model", "True"
    ]
    
    print(f"🎬 Génération vidéo avec Wan 2.2...")
    print(f"📸 Image: {image_path}")
    print(f"💬 Prompt: {prompt}")
    
    # Exécution
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Erreur génération: {result.stderr}")
    
    print(f"✅ Vidéo générée!")
    
    # Trouver la vidéo générée (dernière créée)
    video_files = sorted(Path(OUTPUT_DIR).glob("*.mp4"), key=os.path.getmtime)
    
    if not video_files:
        raise Exception("Aucune vidéo générée")
    
    return str(video_files[-1])

def handler(job):
    """Handler principal pour RunPod"""
    job_input = job["input"]
    
    # Récupérer les paramètres
    image_b64 = job_input.get("image")
    prompt = job_input.get("prompt", "natural camera movement, smooth motion")
    
    if not image_b64:
        return {"error": "No image provided"}
    
    try:
        # Décoder l'image
        if image_b64.startswith('data:image'):
            image_b64 = image_b64.split(',', 1)[1]
        
        image_data = base64.b64decode(image_b64)
        
        # Sauvegarder l'image temporairement
        input_image_path = "/tmp/input_image.png"
        with open(input_image_path, 'wb') as f:
            f.write(image_data)
        
        print(f"📥 Image reçue: {len(image_data)} bytes")
        
        # Générer la vidéo
        video_path = generate_video(input_image_path, prompt)
        
        # Lire et encoder la vidéo
        with open(video_path, 'rb') as f:
            video_data = f.read()
        
        video_b64 = base64.b64encode(video_data).decode('utf-8')
        
        print(f"📤 Vidéo encodée: {len(video_data)} bytes")
        
        return {
            "video": video_b64,
            "format": "mp4",
            "duration": 5,
            "resolution": "1280x720"
        }
    
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

# Démarrer le serveur RunPod
runpod.serverless.start({"handler": handler})
