import asyncio

from src.parser.parser import Parser

parser = Parser()


async def main():
    await parser.start_checking()


if __name__ == "__main__":
    asyncio.run(main())
