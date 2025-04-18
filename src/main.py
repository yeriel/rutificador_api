import re
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configuración de CORS
origins = [
    "https://zqinternet.cl:8082",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_data/{rut}")
async def get_data(rut: str):
    rut_, dv = rut.split('-')
    rut_ = f"{int(rut_):,}".replace(",", ".") + f"-{dv}"
    # The actual API endpoint that returns the data
    url = f"https://r.rutificador.co/pr/{rut_.upper()}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.rutificador.co/",
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3",
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers)
            if response.status_code == 200:
                html = response.text
                # Check if no results were found
                if "No se encontraron resultados" in html:
                    return {"results": []}
                # Parse the HTML response
                pattern = r'<tr>\s*<td>(.*?)</td>\s*<td>(\d{1,2}\.\d{3}\.\d{3}-[\dkK])</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>'
                matches = re.findall(pattern, html, re.DOTALL)
                if matches:
                    results = []
                    for match in matches:
                        results.append({
                            "nombre": match[0].strip(),
                            "rut": match[1],
                            "sexo": match[2].strip(),
                            "direccion": match[3].strip(),
                            "comuna": match[4].strip()
                        })
                    return {"results": results}
                else:
                    raise HTTPException(status_code=404, detail="No se encontraron resultados")
            else:
                raise HTTPException(status_code=response.status_code, detail="Error en la llamada a Rutificador")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Error al realizar la llamada: {str(e)}")

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)