import logging
from typing import Any, Dict, List

from config import settings

LOGGER = logging.getLogger(__name__)


async def create_new_indexes(session, index_definitions: List[Dict[str, Any]]):
    """Create new indexes in the new search service."""
    LOGGER.info(f"Creating {len(index_definitions)} indexes")

    for index in index_definitions:
        index_name = index.get("name")
        if not index_name:
            LOGGER.error("Index definition missing name property")
            continue

        LOGGER.info(f"Creating index: {index_name}")
        endpoint = f"indexes('{index_name}')"

        try:
            async with session.put(
                endpoint, params=settings.create_params, json=index
            ) as response:
                await response.json()
                LOGGER.info(f"Successfully created index: {index_name}")
        except Exception as e:
            LOGGER.error(f"Error creating index {index_name}: {str(e)}")


async def list_indexes(session) -> List[Dict[str, Any]]:
    """List indexes from the old search service."""
    LOGGER.info("Listing indexes")

    # Now using our custom session.get() which adds the api-version
    async with session.get("indexes", params=settings.list_params) as response:
        result = await response.json()
        indexes = result.get("value", [])
        LOGGER.info(f"Found {len(indexes)} indexes")
        return indexes
