import asyncio
import os

TOKEN = os.getenv("BOT_TOKEN")

async def main():
    print("Bot Started Successfully")
    while True:
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
