import asyncio
import aiohttp
import os
import typing

async def ign_to_uuid(session: aiohttp.ClientSession, ign: str) -> str | None:
    async with session.get(f"https://api.mojang.com/users/profiles/minecraft/{ign}") as resp:
        match resp.status:
            case 404:
                return None
            case 200:
                json = await resp.json()
                return json["id"]
            case _:
                raise RuntimeError(
                    f"Mojang API returned status {resp.status} for {ign}")


async def skyblock_profiles(session: aiohttp.ClientSession, uuid: str, key: str) -> typing.Any:
    params = {"uuid": uuid, "key": key}
    async with session.get(f"https://api.hypixel.net/v2/skyblock/profiles", params=params) as resp:
        if resp.status == 200:
            json = await resp.json()
            return json["profiles"]
        else:
            raise RuntimeError(
                f"Hypixel API returned status {resp.status} for {uuid}")


async def main():
    ign = "appable"
    key = os.environ["HYPIXEL_API_KEY"]

    async with aiohttp.ClientSession() as session:
        uuid = await ign_to_uuid(session, "appable")
        profiles = await skyblock_profiles(session, uuid, key)
        print(f"{ign} ({uuid}) has {len(profiles)} profiles")

asyncio.run(main())
