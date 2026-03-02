# CC_phase2_integration
# Process-Industry Integration Service

This project integrates Team 8's Process Definition microservice with Team 10's Industry Connect Service, creating a system where industry partners can be informed about and participate in university quality processes.

## Overview

The integration service acts as middleware between two existing microservices:

- **Team 8's Process Definition service**: Manages university processes and quality assurance procedures
- **Team 10's Industry Connect Service**: Manages relationships with industry partners

## Features

- View all processes from Team 8's service
- View all industry partners from Team 10's service
- Create links between processes and industry partners
- Query which processes a partner is interested in
- Find all partners interested in a specific process

## Project Structure

```
integration_project/
├── docker-compose.yml
├── .env
├── industry_connect_service/    (Team 10's service)
│   ├── app/
│   │   ├── __init__.py
│   │   ├── crud.py
│   │   ├── database.py
│   │   ├── main.py
│   │   ├── models.py
│   │   └── schemas.py
│   ├── Dockerfile
│   ├── requirements.txt
│   └── industry.db
├── microservice/               (Team 8's service)
│   ├── app/
│   ├── .env
│   ├── Dockerfile
│   └── requirements.txt
└── integration_service/        (New integration service)
    ├── integration_service.py
    ├── Dockerfile
    └── requirements.txt
```

## Installation and Setup

1. Clone the repository:
   ```
   git clone [repository URL]
   cd integration_project
   ```

2. Update the `.env` file with appropriate configuration:
   ```
   DATABASE_URL=sqlite:///./integration.db
   PROCESS_SERVICE_URL=http://process-definition-service:8000
   INDUSTRY_SERVICE_URL=http://industry-connect-service:8000
   ```

3. Build and start the services:
   ```
   docker-compose up
   ```

## Usage

Once the services are running, you can access the integration service's API documentation at:
```
http://localhost:8004/docs
```

### Example API Calls

1. View all processes:
   ```
   GET http://localhost:8004/processes/
   ```

2. View all industry partners:
   ```
   GET http://localhost:8004/partners/
   ```

3. Link a process to a partner:
   ```
   POST http://localhost:8004/link/
   {
     "process_id": 1,
     "partner_id": 1
   }
   ```

4. View processes linked to a partner:
   ```
   GET http://localhost:8004/partner/1/processes
   ```

5. View partners linked to a process:
   ```
   GET http://localhost:8004/process/1/partners
   ```

## Technical Implementation

The integration service is built with:
- FastAPI for the REST API framework
- SQLAlchemy for database operations
- HTTPX for asynchronous HTTP requests between services

## Docker Deployment

The services are containerized using Docker and orchestrated with Docker Compose. Each service runs in its own container but can communicate via a shared Docker network.

## Troubleshooting

If you encounter 404 errors when linking processes and partners:
1. Check that both source services are running and accessible
2. Verify that processes and partners with the specified IDs exist
3. Check service logs for more detailed error messages:
   ```
   docker-compose logs integration-service
   ```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request
