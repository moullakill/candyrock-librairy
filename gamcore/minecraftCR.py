import argparse
import asyncio
import sys
import json

# --- CONFIGURATION GCCR (GameCore CandyRock) ---
GCCR_CONFIG = {
    "name": "Minecraft Core",
    "version": "1.1.0",
    "author": "CandyRock Team",
    "description": "Gestionnaire de mods Modrinth pour Minecraft",
    "CRMCP_compatible": True
}

def response_rpc(result=None, error=None, id=1):
    """Formate la sortie au format JSON-RPC pour le protocole CRMCP."""
    response = {
        "jsonrpc": "2.0",
        "id": id
    }
    if error:
        response["error"] = {"code": -32000, "message": error}
    else:
        response["result"] = result
    print(json.dumps(response))

async def run_logic():
    from plugins import init, install, search, candy, lollipop, sugar, clear, list as list_plugin

    parser = argparse.ArgumentParser(prog="candyrock-minecraft", description=GCCR_CONFIG["description"])
    
    # 1. ARGUMENTS GLOBAUX (Placés ici pour être reconnus en début de commande)
    parser.add_argument("-y", "--yes", action="store_true", help="Validation automatique")
    parser.add_argument("-s", "--silent", action="store_true", help="Mode silencieux")
    parser.add_argument("-c", "--config", default="minirock.json", help="Fichier de configuration cible")
    parser.add_argument("--crmcp", action="store_true", help="Active le protocole JSON-RPC")

    subparsers = parser.add_subparsers(dest="command", help="Commandes disponibles")

    # Définition des sous-commandes
    p_init = subparsers.add_parser("init")
    p_init.add_argument("name", nargs="?")
    p_init.add_argument("--mc")
    p_init.add_argument("--loader")
    p_init.add_argument("--path")

    p_search = subparsers.add_parser("search")
    p_search.add_argument("query")

    p_install = subparsers.add_parser("install", help="Installe un ou plusieurs mods")
    p_install.add_argument("project_ids", nargs="+", help="ID(s) du projet Modrinth")

    subparsers.add_parser("list")
    
    p_candy = subparsers.add_parser("candy")
    p_candy.add_argument("-o", "--output", default="recipe.json")

    p_lollipop = subparsers.add_parser("lollipop")
    p_lollipop.add_argument("-o", "--output", default="box.zip")

    p_sugar = subparsers.add_parser("sugar")
    p_sugar.add_argument("source")

    p_clear = subparsers.add_parser("clear")
    p_clear.add_argument("mod", nargs="?")

    args = parser.parse_args()

    # Si CRMCP est actif, on force le mode silent pour ne pas corrompre le JSON
    is_silent = args.silent or args.crmcp

    try:
        res = None
        if args.command == "init":
            res = init.run_init(args.name, args.mc, args.loader, args.path, silent=is_silent)

        elif args.command == "search":
            res = await search.run_search(args.query, args.config, silent=is_silent)

        elif args.command == "install":
            # On passe la liste d'IDs capturée par nargs="+"
            res = await install.install_mod(args.project_ids, args.config, silent=is_silent)

        elif args.command == "list":
            res = list_plugin.run_list(args.config, silent=is_silent)

        elif args.command == "candy":
            res = candy.run_candy(args.config, args.output, silent=is_silent)

        elif args.command == "lollipop":
            res = lollipop.run_lollipop(args.config, args.output, silent=is_silent)

        elif args.command == "sugar":
            res = await sugar.run_sugar(args.source, args.config, silent=is_silent)

        elif args.command == "clear":
        # On ajoute silent=is_silent pour respecter le flag --crmcp
            res = clear.run_clear(args.config, args.mod, force=args.yes, silent=is_silent)

        elif not args.command:
            if args.crmcp:
                response_rpc(result=GCCR_CONFIG)
            else:
                parser.print_help()
            return

        # Gestion de la réponse CRMCP
        if args.crmcp:
            if isinstance(res, dict) and "error" in res:
                response_rpc(error=res["error"])
            else:
                response_rpc(result=res)

    except Exception as e:
        if args.crmcp:
            response_rpc(error=str(e))
        else:
            print(f"❌ Erreur critique : {e}")

def main():
    try:
        asyncio.run(run_logic())
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()