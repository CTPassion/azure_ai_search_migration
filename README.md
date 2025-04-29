# Azure AI Search Migration Tool

Scripts for migrating Azure AI Search (Cognitive) services, including indexes and their data.

## Overview

This tool provides a seamless way to migrate content between Azure AI Search services. It handles:

- Index definitions migration
- Document data migration with pagination
- Bulk uploads for efficient data transfer

## Requirements

- Python 3.8+
- Azure AI Search services (source and target)
- API access keys for both services

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/azure_ai_search_migration.git
cd azure_ai_search_migration
```

2. Set up a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file with your configuration (this will be loaded by Pydantic settings):

```
# API version
API_VERSION=2024-07-01
ALLOW_INDEX_DOWNTIME=true

# Source search service
OLD_SEARCH__SEARCH_SERVICE_NAME=your-source-search-service
OLD_SEARCH__API_KEY=your-source-api-key

# Target search service
NEW_SEARCH__SEARCH_SERVICE_NAME=your-target-search-service
NEW_SEARCH__API_KEY=your-target-api-key
```

## Usage

Run the migration with:

```bash
python main.py
```

The migration process:

1. Retrieves all index definitions from the source service
2. Creates these indexes in the target service
3. Migrates all documents from each index to the target service

## Code Structure

- `main.py` - Main entry point for the migration process
- `config.py` - Configuration handling using Pydantic
- `index_definitions.py` - Code for migrating index definitions
- `index_data.py` - Code for extracting and uploading documents

## Advanced Configuration

### Batch Sizes

You can adjust batch sizes when migrating large indexes by modifying the `batch_size` parameter when calling `migrate_documents()`.

### Error Handling

The application includes comprehensive error handling and logging to help troubleshoot migration issues.

## Troubleshooting

### API Version Issues

Ensure you're using a supported API version for both source and target services.

### Rate Limiting

Azure Search has service limits - if you encounter throttling, try reducing batch sizes or adding delays between requests.

### Authentication Errors

Double-check your API keys and ensure they have appropriate permissions.

## License

See the [LICENSE](LICENSE) file for details.
