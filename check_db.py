import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    db_url = os.getenv('DATABASE_URL').replace('postgresql+asyncpg', 'postgresql')
    print(f"Connecting to {db_url}")
    try:
        conn = await asyncpg.connect(db_url)
        tables = await conn.fetch("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
        print("Tables in public schema:")
        for t in tables:
            print("-", t['table_name'])
        await conn.close()
    except Exception as e:
        print("Error connecting:", e)

asyncio.run(check())
