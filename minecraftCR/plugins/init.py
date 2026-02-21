import os
from core.config_loader import ConfigLoader

def run_init(name=None, mc_version=None, loader=None, path=None, silent=False):
    """
    Initialise une nouvelle instance CandyRock (Minecraft).
    Supporte le mode interactif et le retour de données pour CRMCP.
    """
    if not silent:
        print("🍬 Configuration de votre nouvelle instance CandyRock (Minecraft)\n")

    # Mode interactif uniquement si les arguments obligatoires manquent
    if not name:
        name = input("📦 Nom du profil (ex: survie-1.20) : ").strip() or "instance"
    
    if not mc_version:
        mc_version = input("🎮 Version de Minecraft (ex: 1.20.1) : ").strip()
        if not mc_version:
            return {"error": "La version de Minecraft est obligatoire."}

    if not loader:
        print("⚙️ Loaders disponibles : fabric, forge, neoforge")
        loader = input("👉 Choisir un loader : ").strip().lower()
        if loader not in ["fabric", "forge", "neoforge"]:
            loader = "fabric"

    if not path:
        path = input("📂 Chemin du dossier mods (par défaut: ./mods) : ").strip() or "./mods"

    # Logique technique
    config_filename = name if name.endswith(".json") else f"{name}.json"
    config_path = os.path.join(os.getcwd(), config_filename)
    loader_config = ConfigLoader(config_path)
    
    config_data = {
        "mc_version": mc_version,
        "loader": loader,
        "path": os.path.abspath(path),
        "hashes": {}
    }
    
    try:
        if not os.path.exists(config_data["path"]):
            os.makedirs(config_data["path"])
            
        loader_config.save(config_data)
        
        if not silent:
            print(f"\n✅ Instance '{name}' créée avec succès !")
            print(f"📄 Config : {config_filename} | 📍 Dossier : {config_data['path']}")
        
        # Retour structuré pour minecraftCR.py (interception CRMCP)
        return {
            "status": "success",
            "instance_name": name,
            "config_path": config_path,
            "game_info": {
                "version": mc_version,
                "loader": loader
            }
        }
    except Exception as e:
        return {"error": str(e)}