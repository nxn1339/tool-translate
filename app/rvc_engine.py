import os
import glob
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Base directory for RVC models
APP_DIR = os.path.dirname(os.path.abspath(__file__))
RVC_MODELS_DIR = os.path.join(APP_DIR, "models", "rvc")
RVC_BASE_MODELS_DIR = os.path.join(RVC_MODELS_DIR, "base")

os.makedirs(RVC_MODELS_DIR, exist_ok=True)
os.makedirs(RVC_BASE_MODELS_DIR, exist_ok=True)


def get_rvc_models_dir() -> str:
    return RVC_MODELS_DIR


def scan_rvc_models() -> List[Dict[str, Any]]:
    """
    Scans the app/models/rvc directory for .pth voice model weights and matching .index files.
    Supports flat structure or subfolders (e.g. app/models/rvc/cogaithoatngon/cogaithoatngon.pth).
    """
    if not os.path.exists(RVC_MODELS_DIR):
        return []

    models = []
    # Search for all .pth files recursively in RVC_MODELS_DIR, ignoring base weights
    for root, _, files in os.walk(RVC_MODELS_DIR):
        # Skip base model directory
        if os.path.abspath(root).startswith(os.path.abspath(RVC_BASE_MODELS_DIR)):
            continue

        for file in files:
            if file.endswith(".pth") and not file.startswith("hubert") and not file.startswith("rmvpe"):
                pth_path = os.path.join(root, file)
                model_name = os.path.splitext(file)[0]
                model_id = model_name

                # Check for matching .index file
                # 1. Exact match in same directory
                exact_index = os.path.join(root, f"{model_name}.index")
                index_path = None
                if os.path.exists(exact_index):
                    index_path = exact_index
                else:
                    # 2. Look for index file matching model name or within a dedicated subfolder
                    indices = [
                        os.path.join(root, f) for f in os.listdir(root)
                        if f.endswith(".index") and (model_name.lower() in f.lower() or os.path.abspath(root) != os.path.abspath(RVC_MODELS_DIR))
                    ]
                    if indices:
                        index_path = indices[0]

                size_mb = round(os.path.getsize(pth_path) / (1024 * 1024), 2)
                models.append({
                    "id": model_id,
                    "name": model_name.replace("_", " ").title(),
                    "pth": pth_path,
                    "index": index_path,
                    "size_mb": size_mb,
                    "has_index": bool(index_path)
                })

    models.sort(key=lambda m: m["name"])
    return models


def check_rvc_readiness() -> Dict[str, Any]:
    """
    Checks hardware, torch CUDA support, and base model presence.
    """
    import torch
    cuda_available = torch.cuda.is_available()
    device_name = torch.cuda.get_device_name(0) if cuda_available else "CPU"

    hubert_exists = os.path.exists(os.path.join(RVC_BASE_MODELS_DIR, "hubert_base.pt")) or os.path.exists(os.path.join(RVC_MODELS_DIR, "hubert_base.pt"))
    rmvpe_exists = os.path.exists(os.path.join(RVC_BASE_MODELS_DIR, "rmvpe.pt")) or os.path.exists(os.path.join(RVC_MODELS_DIR, "rmvpe.pt"))

    user_models = scan_rvc_models()

    ready = hubert_exists and rmvpe_exists and len(user_models) > 0

    return {
        "ready": ready,
        "cuda_available": cuda_available,
        "device": device_name,
        "torch_version": torch.__version__,
        "hubert_exists": hubert_exists,
        "rmvpe_exists": rmvpe_exists,
        "models_count": len(user_models),
        "models": user_models
    }


def convert_audio_segment_rvc(
    input_wav: str,
    output_wav: str,
    model_id: str,
    f0_pitch: int = 0,
    f0_method: str = "rmvpe",
    index_rate: float = 0.75,
    filter_radius: int = 3,
    resample_sr: int = 0,
    rms_mix_rate: float = 0.25,
    protect: float = 0.33
) -> bool:
    """
    Converts audio using RVC model.
    If RVC runtime or model is unavailable, gracefully falls back and keeps original audio.
    """
    models = {m["id"]: m for m in scan_rvc_models()}
    if model_id not in models:
        logger.warning(f"RVC model '{model_id}' not found. Falling back to original audio.")
        return False

    model_info = models[model_id]
    pth_path = model_info["pth"]
    index_path = model_info.get("index") or ""

    rvc_root = os.path.abspath(os.path.join(APP_DIR, "..", "rvc_backend"))
    convert_script = os.path.join(rvc_root, "main", "inference", "conversion", "convert.py")
    if not os.path.exists(convert_script):
        logger.error(f"convert.py not found at {convert_script}")
        return False

    import sys
    import subprocess

    env = os.environ.copy()
    env["PYTHONPATH"] = rvc_root

    cmd = [
        sys.executable,
        convert_script,
        "--convert",
        "--input_path", os.path.abspath(input_wav),
        "--output_path", os.path.abspath(output_wav),
        "--pth_path", os.path.abspath(pth_path),
        "--pitch", str(int(f0_pitch)),
        "--f0_method", f0_method,
        "--index_rate", str(index_rate),
        "--filter_radius", str(filter_radius),
        "--rms_mix_rate", str(rms_mix_rate),
        "--protect", str(protect)
    ]
    if index_path and os.path.exists(index_path):
        cmd.extend(["--index_path", os.path.abspath(index_path)])
    else:
        cmd.extend(["--index_path", ""])

    try:
        logger.info(f"RVC converting '{input_wav}' with model '{model_id}' (pitch={f0_pitch})...")
        res = subprocess.run(cmd, env=env, cwd=rvc_root, capture_output=True, text=True)
        if res.returncode == 0 and os.path.exists(output_wav) and os.path.getsize(output_wav) > 1000:
            logger.info(f"RVC successfully converted '{output_wav}' ({os.path.getsize(output_wav)} bytes)")
            return True
        else:
            logger.error(f"RVC conversion error (code {res.returncode}): {res.stderr[:300]}")
            return False
    except Exception as e:
        logger.error(f"Error during RVC conversion: {e}")
        return False

