import os
import json
import zipfile
from core.config_loader import ConfigLoader
from core.manager import FileManager

def get_mod_metadata(jar_path):
    """Extrait le nom et la version du mod depuis fabric.mod.json ou mods.toml."""
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            # Check Fabric
            if "fabric.mod.json" in jar.namelist():
                with jar.open("fabric.mod.json") as f:
                    data = json.load(f)
                    return data.get("name", "Inconnu"), data.get("version", "N/A")
            # Check Forge/NeoForge
            if "META-INF/mods.toml" in jar.namelist():
                return "Mod Forge/NeoForge", "N/A"
    except:
        pass
    return os.path.basename(jar_path), "N/A"

def run_list(config_file, silent=False):
    """Affiche l'état de l'instance et retourne les données structurées."""
    cfg_loader = ConfigLoader(config_file)
    config = cfg_loader.load()
    if not config:
        if not silent: print("❌ Config introuvable.")
        return {"error": "Configuration introuvable"}

    manager = FileManager(config["path"])
    installed_files = manager.list_files(extension=".jar")
    saved_hashes = config.get("hashes", {})
    
    # Préparation des données pour le retour CRMCP
    mods_data = []

    if not silent:
        print(f"\n--- 🛠️ Candyrock Instance : {os.path.basename(config_file)} ---")
        print(f"MC: {config.get('mc_version')} | Loader: {config.get('loader', '').upper()}")
        print("-" * 70)
        print(f"{'NOM DU MOD':<30} | {'VERSION':<15} | {'ÉTAT'}")
        print("-" * 70)

    for jar_name in installed_files:
        full_path = os.path.join(config["path"], jar_name)
        mod_name, mod_ver = get_mod_metadata(full_path)
        
        # Vérification d'intégrité
        current_hash = manager.calculate_sha1(jar_name)
        is_ok = current_hash == saved_hashes.get(jar_name)
        status_str = "✅ OK" if is_ok else "❌ CORROMPU"
        
        # Ajout à la liste structurée
        mods_data.append({
            "name": mod_name,
            "version": mod_ver,
            "file": jar_name,
            "status": "ok" if is_ok else "corrupted"
        })

        if not silent:
            print(f"{mod_name[:28]:<30} | {mod_ver[:13]:<15} | {status_str}")
    
    if not silent:
        print("-" * 70)
        print(f"Total : {len(installed_files)} mods installés.\n")

    # Retourne les données pour le moteur CRMCP
    return {
        "instance": os.path.basename(config_file),
        "count": len(mods_data),
        "mods": mods_data
    }