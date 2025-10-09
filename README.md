# KarmaChain v2.1

A comprehensive karma tracking system with unified event processing, file upload support, and multi-department integration capabilities.

## Key Features

- **Unified Event Gateway**: Single endpoint for all karma operations
- **File Upload System**: Secure file upload with validation and storage
- **Event Audit Trail**: Complete event logging and lifecycle tracking
- **Docker Containerization**: Full containerized deployment with MongoDB
- **Multi-Department Support**: Analytics (BHIV), Infrastructure (Unreal), API Integration (Knowledgebase)
- **Comprehensive Testing**: Unit, integration, and file upload tests
- **Versioned API Endpoints**: Consistent API versioning for stability

## Quick Start

### Using Docker (Recommended)

1. Clone the repository
2. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```
3. Start the application:
   ```
   docker-compose up -d
   ```
4. Access the API at `http://localhost:8000`
5. View API documentation at `http://localhost:8000/docs`

### Manual Setup

1. Clone the repository
2. Create a virtual environment:
   ```
   python -m venv myenv
   source myenv/bin/activate  # On Windows: myenv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Configure environment variables:
   ```
   cp .env.example .env
   # Edit .env with your configuration
   ```
5. Start the application:
   ```
   uvicorn main:app --reload
   ```

## API Documentation

- [API Documentation](docs/api_documentation.md) - Complete API reference
- [Unified Event API](docs/unified_event_api.md) - Unified event gateway guide
- [KarmaChain v2 Guide](docs/karmachain_v2.md) - System overview and architecture
- [Handover Guide](docs/HANDOVER_GUIDE.md) - Deployment and integration guide

## Testing

Run integration tests to verify system functionality:

```bash
# Using the provided test script
python tests/integration_demo.py

# Or using the Docker setup script
./scripts/run_local.sh
```

## System Status

✅ **Handover Ready** - System is fully implemented and ready for production deployment

- Unified Event Gateway: ✅ Implemented
- File Upload System: ✅ Implemented  
- Event Audit Trail: ✅ Implemented
- Docker Environment: ✅ Implemented
- Multi-Department Support: ✅ Implemented
- Comprehensive Testing: ✅ Implemented

## Integration Guide

### Unified Event Gateway

The recommended way to integrate with KarmaChain is through the unified event gateway:

```
POST /v1/karma/event
{
  "event_type": "life_event",
  "user_id": "user123",
  "data": {
    "role": "human",
    "action": "help",
    "description": "Helped a colleague with debugging"
  }
}
```

This endpoint accepts various event types and routes them internally, providing a consistent integration point for all departments.

### File Upload Support

Upload files as evidence for atonement events:

```
POST /v1/karma/event/with-file
Form Data:
  - event_data: JSON string with event details
  - file: Upload file (jpg, jpeg, png, pdf, doc, docx)
```

### Supported Event Types

- `life_event`: Log karma actions and behaviors
- `appeal`: Submit karma appeals
- `atonement`: Request and complete atonement plans
- `atonement_with_file`: Atonement with supporting evidence files
- `death_event`: Record death events for karma transfer
- `stats_request`: Query user karma statistics

## Directory Structure

```
├── data/                  # Data files and vedic corpus
├── docs/                  # API documentation and guides
├── routes/                # API routes
│   └── v1/                # Version 1 API
│       └── karma/         # Karma-related endpoints
├── utils/                 # Utility functions (atonement, merit, paap, etc.)
├── scripts/               # Setup and utility scripts
├── tests/                 # Integration and unit tests
├── uploads/               # File upload storage
├── backups/               # System backups
├── logs/                  # Application logs
├── mongo-init/            # MongoDB initialization scripts
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose configuration
├── main.py                # Application entry point
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── system_manifest.json   # System configuration and status
```

## License

Proprietary - All rights reserved
