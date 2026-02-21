import asyncio
import json  # <--- AJOUT INDISPENSABLE
from core.api import ModrinthAPI
from core.config_loader import ConfigLoader

async def run_search(query, config_file=None, limit=10, silent=False):
    """
    Interroge l'API Modrinth et retourne les résultats.
    """
    api = ModrinthAPI()
    filters = None

    # Application des filtres contextuels basés sur la config
    if config_file:
        cfg_loader = ConfigLoader(config_file)
        cfg = cfg_loader.load()
        if cfg:
            # Format JSON strict pour Modrinth : [["versions:1.20.1"], ["categories:fabric"]]
            facets_list = [
                [f"versions:{cfg.get('mc_version')}"],
                [f"categories:{cfg.get('loader')}"]
            ]
            filters = json.dumps(facets_list)

    if not silent:
        print(f"🔍 Recherche de '{query}' sur Modrinth...")
    
    try:
        raw_results = await api.search_mods(query, filters=filters)
        
        if not raw_results:
            if not silent: print("❌ Aucun mod trouvé.")
            return {"status": "success", "count": 0, "results": []}

        formatted_results = []
        for hit in raw_results[:limit]:
            mod_data = {
                "title": hit.get("title"),
                "project_id": hit.get("project_id"),
                "author": hit.get("author"),
                "description": hit.get("description"),
                "slug": hit.get("slug")
            }
            formatted_results.append(mod_data)

        if not silent:
            print(f"\n{'NOM':<30} | {'ID PROJET':<15} | {'AUTEUR'}")
            print("-" * 65)
            for mod in formatted_results:
                display_title = (mod['title'][:27] + '..') if len(mod['title']) > 27 else mod['title']
                print(f"{display_title:<30} | {mod['project_id']:<15} | {mod['author']}")
            
            print(f"\n💡 Installation : candyrock install {formatted_results[0]['project_id']}")

        return {
            "status": "success",
            "count": len(formatted_results),
            "results": formatted_results
        }

    except Exception as e:
        if not silent: print(f"❌ Erreur API : {e}")
        return {"status": "error", "message": str(e)}