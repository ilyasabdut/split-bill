import asyncio

from sqlalchemy.ext.asyncio import create_async_engine


async def test_connection(host="localhost"):
    url = f"postgresql+asyncpg://postgres:postgres@{host}:5432/splitbill"
    print(f"Testing connection to {url}...")
    engine = create_async_engine(url)
    try:
        async with engine.connect():
            print(f"Successfully connected to {host}!")
    except Exception as e:
        print(f"Connection to {host} failed: {e}")
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(test_connection("localhost"))
    asyncio.run(test_connection("127.0.0.1"))
