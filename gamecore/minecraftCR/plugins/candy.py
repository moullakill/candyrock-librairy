import os
import json
from core.config_loader import ConfigLoader

def run_candy(config_file, output_name="recipe.json"):
    """
    Génère un manifeste JSON (recipe) de l'instance actuelle.
    """
    cfg_loader = ConfigLoader(config_file)
    config = cfg_loader.load()
    
    if not config:
        return {"error": "Configuration introuvable"}

    # Structure de la recette CandyRock
    recipe = {
        "gamecore": "minecraft",
        "metadata": {
            "mc_version": config.get("mc_version"),
            "loader": config.get("loader")
        },
        "content": config.get("hashes", {})
    }

    output_path = os.path.join(os.getcwd(), output_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(recipe, f, indent=4)
    
    # Message console pour l'humain
    print(f"🍬 Recipe générée : {output_name}")
    
    # Retour pour CRMCP
    return {
        "status": "success",
        "recipe_path": output_path,
        "mod_count": len(recipe["content"])
    }
