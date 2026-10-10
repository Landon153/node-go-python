import asyncio
import json

async def main():
    limit = asyncio.Semaphore(2)
    active = 0
    max_active = 0
    async def job(index):
        nonlocal active, max_active
        async with limit:
            active += 1
            max_active = max(max_active, active)
            try:
                await asyncio.sleep(0.03)
                return index * 2
            finally:
                active -= 1
    values = await asyncio.gather(*(job(i) for i in range(6)))
    print(json.dumps({"values": values, "max_active": max_active}))

asyncio.run(main())
