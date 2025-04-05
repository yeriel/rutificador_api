import re
import httpx
import uvicorn
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/get_data/{rut}")
async def get_data(rut: str):
    rut_, dv = rut.split('-')
    rut_ = f'{rut[-7:]}.{rut[-4:-7]}.{rut[-1:-4]}-{dv}'
    
    # The actual API endpoint that returns the data
    url = f"https://r.rutificador.co/pr/{rut_.upper()}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Referer": "https://www.rutificador.co/",
        "X-Requested-With": "XMLHttpRequest"
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