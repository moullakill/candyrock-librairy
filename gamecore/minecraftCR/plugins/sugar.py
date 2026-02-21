import os
import zipfile
import json
from core.config_loader import ConfigLoader

async def run_sugar(source_path, target_config, silent=False):
    """
    Déploie une instance à partir d'un fichier .json (recipe) ou .zip (lollipop).
    """
    if not os.path.exists(source_path):
        if not silent: print(f"❌ Fichier source introuvable : {source_path}")
        return {"status": "error", "message": "source_not_found"}

    cfg_loader = ConfigLoader(target_config)
    cfg = cfg_loader.load()
    
    if not cfg:
        if not silent: print("❌ Configuration cible introuvable.")
        return {"status": "error", "message": "config_not_found"}

    try:
        # CAS 1 : Recette JSON
        if source_path.endswith(".json"):
            if not silent: print(f"🍬 Application de la recette : {source_path}")
            
            with open(source_path, 'r') as f:
                recipe = json.load(f)
            
            # Ici, on pourrait implémenter une boucle de restauration via install_mod
            # Pour l'instant, on valide juste la lecture
            if not silent: print("♻️ Analyse de la recette terminée.")
            return {"status": "success", "type": "recipe", "mods_count": len(recipe.get("hashes", {}))}

        # CAS 2 : Boîte ZIP (Lollipop)
        elif source_path.endswith(".zip"):
            if not silent: print(f"🍭 Déballage de la boîte : {source_path}")
            
            with zipfile.ZipFile(source_path, 'r') as zipf:
                # On extrait dans le dossier parent du dossier mods pour recréer la structure
                extract_path = os.path.dirname(os.path.abspath(cfg["path"]))
                zipf.extractall(extract_path)
            
            if not silent: print("✅ Instance déployée avec succès.")
            return {"status": "success", "type": "box", "target": extract_path}

        else:
            return {"status": "error", "message": "unsupported_format"}

    except Exception as e:
        if not silent: print(f"❌ Erreur lors du déploiement : {e}")
        return {"status": "error", "message": str(e)}