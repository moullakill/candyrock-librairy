import httpx

class ModrinthAPI:
    BASE_URL = "https://api.modrinth.com/v2"

    def __init__(self):
        # User-Agent mis à jour pour refléter le nouveau nom du projet
        self.headers = {"User-Agent": "CandyRock-Minecraft/1.0.0"}

    async def search_mods(self, query, filters=None):
        params = {"query": query, "index": "relevance"}
        if filters:
            params["facets"] = filters
        
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(f"{self.BASE_URL}/search", params=params)
            response.raise_for_status()
            return response.json()["hits"]

    async def get_project_versions(self, project_id, loader=None, mc_version=None):
        params = {}
        if loader: params["loaders"] = f'["{loader}"]'
        if mc_version: params["game_versions"] = f'["{mc_version}"]'
        
        async with httpx.AsyncClient(headers=self.headers) as client:
            response = await client.get(f"{self.BASE_URL}/project/{project_id}/version", params=params)
            response.raise_for_status()
            return response.json()

    async def download_file(self, url, dest_path, progress_callback=None):
        """Télécharge un fichier avec support de notification pour CRMCP."""
        async with httpx.AsyncClient(headers=self.headers) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                with open(dest_path, "wb") as f:
                    async for chunk in response.aiter_bytes():
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total > 0:
                            # Envoie un pourcentage pour le flux JSON-RPC
                            progress_callback(int((downloaded / total) * 100))
