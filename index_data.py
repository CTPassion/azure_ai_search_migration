import logging
from typing import Any, Dict, List

from config import settings

LOGGER = logging.getLogger(__name__)


async def get_all_documents(
    session, index_name: str, batch_size: int = 1000
) -> List[Dict[str, Any]]:
    """
    Extract all documents from an index using pagination.

    Args:
        session: The aiohttp ClientSession to use
        index_name: The name of the index to extract from
        batch_size: Number of documents to retrieve per page

    Returns:
        A list of all documents from the index
    """
    LOGGER.info(f"Extracting all documents from index {index_name}")
    all_documents = []

    # Search query to get all documents
    search_query = {
        "search": "*",  # Search everything
        "top": batch_size,
        "skip": 0,
        "select": "*",  # Get all fields
    }

    while True:
        try:
            # Send search request
            endpoint = f"indexes/{index_name}/docs/search"
            async with session.post(
                endpoint, params=settings.search_params, json=search_query
            ) as response:
                results = await response.json()

                # Get the documents from the current page
                documents = results.get("value", [])

                # Remove the @search.* metadata fields
                documents = [
                    {k: v for k, v in doc.items() if not k.startswith("@search.")}
                    for doc in documents
                ]

                if not documents:
                    # No more documents, exit the loop
                    break

                # Add the documents to our collection
                all_documents.extend(documents)
                LOGGER.info(
                    f"Retrieved {len(documents)} documents from index {index_name}, total so far: {len(all_documents)}"
                )

                # Check if we've reached the end
                if len(documents) < batch_size:
                    break

                # Update the skip value for the next page
                search_query["skip"] += batch_size

        except Exception as e:
            LOGGER.error(
                f"Error retrieving documents from index {index_name}: {str(e)}"
            )
            break

    LOGGER.info(
        f"Extracted {len(all_documents)} documents total from index {index_name}"
    )
    return all_documents


def prepare_bulk_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Format documents for bulk upload according to Azure Search API requirements.

    Args:
        documents: List of documents to format

    Returns:
        Formatted documents for bulk upload with @search.action
    """
    bulk_documents = []

    for doc in documents:
        # Create a copy of the document
        doc_copy = doc.copy()

        # Add the @search.action field
        doc_copy["@search.action"] = "upload"

        bulk_documents.append(doc_copy)

    return bulk_documents


async def upload_documents_in_batches(
    session, index_name: str, documents: List[Dict[str, Any]], batch_size: int = 1000
):
    """
    Upload documents to the target index in batches using bulk upload.

    Args:
        session: The aiohttp ClientSession to use
        index_name: The name of the index to upload to
        documents: The documents to upload
        batch_size: Number of documents per batch
    """
    LOGGER.info(
        f"Uploading {len(documents)} documents to index {index_name} in batches of {batch_size}"
    )

    # Process documents in batches
    for i in range(0, len(documents), batch_size):
        batch = documents[i : i + batch_size]
        batch_num = (i // batch_size) + 1

        LOGGER.info(f"Processing batch {batch_num} with {len(batch)} documents")

        # Format documents for bulk upload
        bulk_batch = prepare_bulk_documents(batch)

        # Send the bulk request
        try:
            endpoint = f"indexes/{index_name}/docs/index"
            async with session.post(
                endpoint, params=settings.upload_params, json={"value": bulk_batch}
            ) as response:
                await response.json()
                LOGGER.info(
                    f"Batch {batch_num} result: {len(bulk_batch)} documents processed"
                )
        except Exception as e:
            LOGGER.error(
                f"Error uploading batch {batch_num} to index {index_name}: {str(e)}"
            )

    LOGGER.info(f"Completed uploading documents to index {index_name}")


async def migrate_documents(
    source_session, target_session, index_name: str, batch_size: int = 1000
):
    """
    Migrate all documents from a source index to a target index.

    Args:
        source_session: The session for the source search service
        target_session: The session for the target search service
        index_name: The name of the index (must be the same in both services)
        batch_size: The batch size for uploads
    """
    LOGGER.info(f"Starting document migration for index {index_name}")

    # Get all documents from the source index
    documents = await get_all_documents(source_session, index_name)

    if not documents:
        LOGGER.info(f"No documents found in source index {index_name}")
        return

    # Upload all documents to the target index
    await upload_documents_in_batches(target_session, index_name, documents, batch_size)

    LOGGER.info(
        f"Completed migration of {len(documents)} documents for index {index_name}"
    )
