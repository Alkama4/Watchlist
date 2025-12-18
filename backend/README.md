# Backend

## Running the development server

### Initial setup

1. Setup the `.env` file

    Create a copy of `.env.loca.example` called `.env.local` and update the details to match your setup.

2. Run the following commands

    Navigate to the backend directory:

    ```bash
    cd backend
    ```

    Install dependencies:

    ```bash
    pip install -r requirements.txt
    ```

    Launch the application:

    ```bash
    uvicorn app.main:app --reload
    ```

    **OR** you can do it all in one command:

    ```bash
    cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload
    ```

### Subsequent Runs

After the initial setup, you can quickly start the server:

```bash
cd backend
uvicorn app.main:app --reload
```
