import os
import json
from core.api import ModrinthAPI
from core.manager import FileManager
from core.config_loader import ConfigLoader

async def install_mod(project_ids, config_file, silent=False):
    """
    Point d'entrée : accepte un ID unique (string) ou une liste d'IDs.
    """
    # Normalisation : si on reçoit un seul ID, on le met en liste
    if isinstance(project_ids, str):
        project_ids = [project_ids]

    results = []
    for pid in project_ids:
        res = await _process_install(pid, config_file, silent)
        if res:
            results.append(res)
    
    return results

async def _process_install(project_id, config_file, silent=False):
    """
    Logique d'installation individuelle et récursive.
    """
    api = ModrinthAPI()
    cfg_loader = ConfigLoader(config_file)
    config = cfg_loader.load()
    
    if not config:
        return None

    manager = FileManager(config["path"])
    
    # Éviter la réinstallation si déjà présent dans la config
    # (Simple check par ID ou hash ici, idéalement)

    # 1. Récupérer les versions compatibles
    try:
        versions = await api.get_project_versions(
            project_id, 
            loader=config["loader"], 
            mc_version=config["mc_version"]
        )
    except Exception as e:
        if not silent: print(f"❌ Erreur API pour {project_id} : {e}")
        return None
    
    if not versions:
        if not silent: print(f"❌ Aucune version compatible trouvée pour {project_id}")
        return None

    target_version = versions[0]
    primary_file = next((f for f in target_version["files"] if f["primary"]), target_version["files"][0])
    
    filename = primary_file["filename"]
    download_url = primary_file["url"]
    expected_hash = primary_file["hashes"]["sha1"]

    # 2. Téléchargement
    dest_path = os.path.join(config["path"], filename)
    if not silent: print(f"📦 Téléchargement de {filename}...")
    await api.download_file(download_url, dest_path)

    # 3. Vérification et Config
    actual_hash = manager.calculate_sha1(filename)
    if actual_hash == expected_hash:
        cfg_loader.update_hash(filename, actual_hash)
    else:
        if not silent: print(f"⚠️ Erreur de hash pour {filename}")

    # 4. Dépendances récursives
    for dep in target_version.get("dependencies", []):
        if dep.get("dependency_type") == "required":
            dep_id = dep["project_id"]
            # Appel récursif interne
            await _process_install(dep_id, config_file, silent)

    return filename
    return results