import os
import zipfile
from core.config_loader import ConfigLoader

def run_lollipop(config_file, output_name="box.zip", silent=False):
    """
    Archive l'instance complète (mods, config, manifest) dans un .zip.
    """
    cfg_loader = ConfigLoader(config_file)
    config = cfg_loader.load()
    
    if not config:
        return {"error": "Configuration introuvable."}

    mods_path = config.get("path")
    # Dossier parent pour localiser le dossier /config de Minecraft
    root_path = os.path.dirname(mods_path)
    minecraft_config_path = os.path.join(root_path, "config")
    
    output_path = os.path.join(os.getcwd(), output_name)

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # 1. Archivage du manifest de l'instance (.json)
            # Permet de reconstruire l'état exact lors de l'extraction
            zipf.write(config_file, os.path.basename(config_file))

            # 2. Archivage des mods (.jar)
            if os.path.exists(mods_path):
                for root, _, files in os.walk(mods_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("mods", os.path.relpath(file_path, mods_path))
                        zipf.write(file_path, arcname)
            
            # 3. Archivage du dossier /config (fichiers de réglages des mods)
            if os.path.exists(minecraft_config_path):
                for root, _, files in os.walk(minecraft_config_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.join("config", os.path.relpath(file_path, minecraft_config_path))
                        zipf.write(file_path, arcname)

        if not silent:
            print(f"🍭 Lollipop (Box) créée avec succès : {output_name}")

        return {
            "status": "success",
            "package_name": output_name,
            "path": output_path,
            "included_mods": len(config.get("hashes", {}))
        }

    except Exception as e:
        return {"error": str(e)}