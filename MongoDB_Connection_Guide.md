# MongoDB Connection Guidance

The application is configured to connect to a local MongoDB instance. If you encounter connection issues, please follow these steps:

## Starting the MongoDB Service
Ensure that your MongoDB server is installed and running on your local machine.
- **Windows**: Search for `Services` in the start menu, find `MongoDB Server`, right-click, and select `Start`.
- **macOS/Linux**: Run `sudo systemctl start mongod` or similar depending on your service manager.

## Connection String
By default, the application uses `mongodb://localhost:27017/`. 
If your MongoDB runs on a different port or requires authentication, you can configure it via environment variables.

## Configuration inside the Project
The connection details are handled in `database.py`. You can explicitly set your connection string by exporting the `MONGO_URI` environment variable before running the Flask application:

```bash
# Windows (PowerShell)
$env:MONGO_URI="mongodb://username:password@localhost:27017/"

# macOS / Linux
export MONGO_URI="mongodb://username:password@localhost:27017/"
```

If the environment variable is not set, it defaults to the unauthenticated local connection.
