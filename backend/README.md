# Backend

## Running the development server

### Initial setup

1. **Setup the `.env` file**

    Create a copy of `.env.loca.example` called `.env.local` and update the details to match your setup.

2. **Create the python virtual environment**

    Navigate to the backend directory in a command line if not already:

    ```bash
    cd backend
    ```

    Setup and active python virtual enviroment:

    ```bash
    # Create
    python -m venv venv

    # Activate
    source venv/bin/activate    # Linux/MacOS
    venv/scripts/activate       # Windows
    ```

3. **Install dependencies**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the alembic migration to setup DB**

    ```bash
    alembic upgrade head
    ```

5. **Launch the application:**

    ```bash
    uvicorn app.main:app --reload --host 0.0.0.0
    ```

### Subsequent Runs

After the initial setup, you can quickly start the server with this:

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0
```

or by using the VS Code task (`Ctrl + Shift + P` -> `Tasks: Run tasks` -> `Dev Server - FastAPI`).


## Alembic migrations

Whenever the `/backend/app/models.py` modified either by adding new models or by modifying the current ones, a new alembic migration needs to be generated.

1. **Generate a new migration script**

    Once you are happy with your changes you can generate a new migration script with the following:

    ```bash
    alembic revision --autogenerate -m "Describe your changes here"
    ```

2. **Apply the migration to your database**

    Inspect the created migration script in `/backend/alembic/versions/` and ensure that it was created successfully. If it was you can apply the changes to your database with this:

    ```bash
    alembic upgrade head
    ```
