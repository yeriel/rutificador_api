import httpx
import uvicorn
import re
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/get_data/{rut}")
async def get_data(rut: str):
    url = f"https://r.rutificador.co/pr/{rut}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers)
            
            if response.status_code == 200:
                html = response.text
                
                pattern = r'<tr>\s*<td>(.*?)</td>\s*<td>(\d{1,2}\.\d{3}\.\d{3}-\d)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*<td>(.*?)</td>\s*</tr>'
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