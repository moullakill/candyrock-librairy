import os
from core.config_loader import ConfigLoader
from core.manager import FileManager

def run_clear(config_file, target=None, force=False, silent=False):
    """
    Supprime les fichiers du dossier cible et nettoie la config.
    Garantit l'absence de prints ou d'inputs en mode silent.
    """
    cfg_loader = ConfigLoader(config_file)
    config = cfg_loader.load()
    
    if not config:
        if not silent:
            print("❌ Configuration introuvable.")
        return {"status": "error", "message": "config_not_found"}

    # Sécurité sur le chemin
    folder_path = config.get("path")
    if not folder_path or not os.path.exists(folder_path):
        if not silent:
            print(f"⚠️ Chemin invalide : {folder_path}")
        return {"status": "error", "message": "invalid_path", "path": folder_path}

    manager = FileManager(folder_path)
    
    # --- CAS 1 : Suppression d'un fichier spécifique ---
    if target:
        if not target.endswith(".jar"):
            target = f"{target}.jar"
            
        if manager.remove_file(target):
            # Mise à jour des hashes dans la config
            if "hashes" in config and target in config["hashes"]:
                del config["hashes"][target]
                cfg_loader.save(config)
            
            if not silent:
                print(f"🗑️ Supprimé : {target}")
            
            return {"status": "success", "action": "deleted", "file": target}
        else:
            if not silent:
                print(f"⚠️ Fichier introuvable : {target}")
            return {"status": "error", "message": "file_not_found", "file": target}

    # --- CAS 2 : Purge totale du dossier ---
    else:
        # En mode CRMCP/silent ou si --yes est utilisé, on ne demande pas de confirmation
        if not force and not silent:
            try:
                confirm = input(f"❗ Vider le dossier {folder_path} ? (y/n) : ")
                if confirm.lower() != 'y':
                    return {"status": "aborted", "message": "user_cancelled"}
            except EOFError:
                # Gère le cas où input() est appelé dans un environnement sans terminal
                return {"status": "error", "message": "no_terminal_input"}

        files = manager.list_files(extension=".jar")
        removed_count = 0
        
        for f in files:
            if manager.remove_file(f):
                removed_count += 1
            
        # Reset complet des hashes
        config["hashes"] = {}
        cfg_loader.save(config)
        
        if not silent:
            print(f"✨ Nettoyage terminé ({removed_count} fichiers).")
            
        return {
            "status": "success", 
            "action": "cleared", 
            "count": removed_count,
            "path": folder_path
        }