import httpx
import asyncio
import json

async def test():
    print("Probando endpoint /insights/generate-daily-summary...")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post('http://127.0.0.1:8001/insights/generate-daily-summary', timeout=60.0)
            print(f"Status: {r.status_code}")
            if r.status_code == 201:
                print("Resumen generado exitosamente!")
                print(json.dumps(r.json(), indent=2))
            else:
                print(f"Error: {r.text}")
    except Exception as e:
        print(f"Error de conexión: {e}")

if __name__ == "__main__":
    asyncio.run(test())
