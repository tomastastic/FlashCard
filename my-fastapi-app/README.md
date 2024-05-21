# API WORK IN PROGRESS

This directory is for the FastAPI application that provides CRUD (Create, Read, Update, Delete) operations on the MySQL database that stores the study resources and the users data. 

## Project Structure

The project has the following file structure:

```
my-fastapi-app
├── app
│   ├── main.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── models.py
│   ├── database
│   │   ├── __init__.py
│   │   └── db.py
│   └── schemas
│       ├── __init__.py
│       └── schemas.py
├── requirements.txt
└── README.md
```

- `app/main.py`: This file is the entry point of the FastAPI application. It creates an instance of the FastAPI app and sets up the routes using the `api.routes` module.

- `app/api/__init__.py`: This file is an empty file that marks the `api` directory as a Python package.

- `app/api/routes.py`: This file exports the API routes for the CRUD operations on the MySQL database. It defines the HTTP endpoints and their corresponding handlers for creating, reading, updating, and deleting data.

- `app/api/models.py`: This file exports the database models for the MySQL tables. It defines the structure and relationships of the data stored in the database.

- `app/database/__init__.py`: This file is an empty file that marks the `database` directory as a Python package.

- `app/database/db.py`: This file exports the database connection and helper functions for interacting with the MySQL database. It establishes the connection, executes queries, and handles transactions.

- `app/schemas/__init__.py`: This file is an empty file that marks the `schemas` directory as a Python package.

- `app/schemas/schemas.py`: This file exports the Pydantic schemas for the data models used in the API. It defines the structure and validation rules for the request and response data.

- `requirements.txt`: This file lists the Python dependencies required for the project. It specifies the packages and their versions that need to be installed.

## Getting Started

To set up and run the FastAPI API for CRUD operations on a MySQL database, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/my-fastapi-app.git
   ```

2. Navigate to the project directory:

   ```bash
   cd my-fastapi-app
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the FastAPI application:

   ```bash
   uvicorn app.main:app --reload
   ```

5. The API is now running and can be accessed at `http://localhost:8000`.

## API Endpoints

The following API endpoints are available:

- `GET /items`: Retrieves all items from the database.
- `GET /items/{item_id}`: Retrieves a specific item by its ID.
- `POST /items`: Creates a new item in the database.
- `PUT /items/{item_id}`: Updates an existing item in the database.
- `DELETE /items/{item_id}`: Deletes an item from the database.

Please refer to the `app/api/routes.py` file for more details on the API endpoints and their usage.

## Database Configuration

The MySQL database connection details can be configured in the `app/database/db.py` file. Update the `DATABASE_URL` variable with your MySQL database connection string.


## License

This project is licensed under the [MIT License](LICENSE).

