import asyncio
import logging

import aiohttp

import index_data
import index_definitions
from config import settings

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


async def main():
    # Create sessions without params (we'll add params to each request instead)
    old_search_session = aiohttp.ClientSession(
        base_url=settings.old_search.search_service_url,
        headers=settings.old_search.search_service_headers,
        raise_for_status=True,
    )

    new_search_session = aiohttp.ClientSession(
        base_url=settings.new_search.search_service_url,
        headers=settings.new_search.search_service_headers,
        raise_for_status=True,
    )

    async with old_search_session, new_search_session:
        # Step 1: Get all index definitions from source
        LOGGER.info("Step 1: Getting index definitions from source")
        old_index_definitions = await index_definitions.list_indexes(old_search_session)

        if not old_index_definitions:
            LOGGER.warning("No indexes found in source search service")
            return

        # Step 2: Create the indexes in the target service
        LOGGER.info("Step 2: Creating indexes in target service")
        # await index_definitions.create_new_indexes(new_search_session, old_index_definitions)

        # Step 3: Migrate documents for each index
        LOGGER.info("Step 3: Migrating documents")
        for index in old_index_definitions:
            index_name = index.get("name")
            if not index_name:
                continue

            LOGGER.info(f"Migrating documents for index: {index_name}")
            try:
                await index_data.migrate_documents(
                    old_search_session, new_search_session, index_name, batch_size=1000
                )
            except Exception as e:
                LOGGER.error(
                    f"Error migrating documents for index {index_name}: {str(e)}"
                )

        LOGGER.info("Migration complete!")


if __name__ == "__main__":
    asyncio.run(main())
