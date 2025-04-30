# Autoclean, SEGP (Group 6)

Automated Data Cleaning for High-Quality ML Training Data

---

## Project Overview

Autoclean is a full-stack application designed for automated data cleaning to ensure high-quality machine learning training data. It consists of:

- **Frontend**: Built with React, providing an intuitive user interface for interacting with the application.
- **Backend**: Powered by Django, handling the core logic, API endpoints, and database interactions.
- **Redis**: Used as a message broker for Celery to manage background tasks such as data processing and seeding.
- **PostgreSQL**: A robust relational database used to store and manage application data efficiently.
- **Celery**: Integrated with Redis to handle asynchronous tasks and background job processing.

---

## Project Structure

```
.
├── backend/       # Backend code (Django)
├── frontend/      # Frontend code (React)
├── notebooks/     # Jupyter notebooks for testing
```

---

## Prerequisites

Ensure you have the following installed:

- **Node.js** (v16 or higher)
- **Python** (v3.9 or higher)
- **Docker** and **Docker Compose**
- **PostgreSQL** (if not using Docker)

---

## Recommended Setup: Running with Docker

For an easier and faster setup, it is recommended to run the **backend** using Docker. The **frontend** must be set up manually as it is not included in the Docker configuration.

### Backend Setup with Docker

1. **Set up environment variables**:
   - Ensure that the `.env` file for the backend is properly configured before building the Docker containers.
   - For the backend:
     - Copy `.env.example` to `.env`:
       ```bash
       cp backend/autoclean/.env.example backend/autoclean/.env
       ```
     - Update the `.env` file with your database and other configurations.

2. **Build and start the backend containers**:
   ```bash
   docker-compose up --build
   ```

3. **Perform migrations and seeding**:
   After starting the containers, you need to manually perform database migrations and seeding:
   - Enter the Django container:
     ```bash
     docker exec -it django bash
     ```
   - Run migrations:
     ```bash
     python manage.py migrate
     ```
     > **Note**: You do not need to run `makemigrations` unless you have made changes to the models. The migration files are already included in the project.
   - Seed the database:
     ```bash
     python manage.py seed_db
     ```

4. **Access the backend**:
   - Backend: [`http://localhost:8000`](http://localhost:8000)

> **Important**: Migrations and seeding are not automated in the current Docker setup. You must perform these steps manually after starting the containers.

---

## Frontend Setup

Since the frontend is not included in the Docker setup, follow these steps to set it up manually:

1. Navigate to the frontend directory:
   ```bash
   cd frontend/autoclean
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   - For development (`npm run dev`):
     - Ensure the `.env.development` file exists in the `frontend/autoclean` directory.
     - Update `.env.development` with the backend API URL and other configurations.

   - For production (`npm run build`):
     - Ensure the `.env.production` file exists in the `frontend/autoclean` directory.
     - Update `.env.production` with the backend API URL and other configurations.

4. Start the development server:
   ```bash
   npm run dev
   ```

5. Build for production:
   ```bash
   npm run build
   ```

6. Serve the production build (optional):
   ```bash
   npm install -g serve
   serve -s build
   ```

---

## Manual Setup

If you prefer to set up the project manually, follow the steps below.

---

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment and activate it:
   - Create the virtual environment in the `backend` directory:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     ```bash
     source venv/bin/activate  # On Windows: venv\Scripts\activate
     ```

3. Install dependencies:
   - Ensure you are in the `backend` directory where the `requirements.txt` file is located:
     ```bash
     pip install -r requirements.txt
     ```

4. Navigate to the Django project directory:
   ```bash
   cd autoclean
   ```

5. Set up environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Update the `.env` file with your database and other configurations.

6. Generate migration files:
   ```bash
   python manage.py makemigrations
   ```

7. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

8. Start the backend server:
   ```bash
   python manage.py runserver
   ```

9. Start Celery workers for background tasks:
   ```bash
   celery -A autoclean worker -B -l info
   ```

---

## Database Migrations and Seeders

### Migrations

Migrations are used to apply changes to the database schema, such as creating tables or modifying fields.

1. **Create a new migration**:
   If you make changes to your models, generate a new migration file:
   ```bash
   python manage.py makemigrations
   ```

2. **Apply migrations**:
   Apply the generated migrations to the database:
   ```bash
   python manage.py migrate
   ```

3. **Check migration status**:
   To see the current migration status:
   ```bash
   python manage.py showmigrations
   ```

---

## Database Seeders

Seeders are used to populate the database with initial or sample data.

1. **Seeder Command**:
   The `seed_db` command is used to seed the database with initial data. It is located in:
   ```
   backend/autoclean/autoclean/management/commands/seed_db.py
   ```

2. **Run the Seeder**:
   Execute the `seed_db` command to populate the database:
   ```bash
   python manage.py seed_db
   ```

3. **What It Does**:
   - Creates a superuser using the `UserSeeder.createsuperuser()` method.
   - Seeds 10 sample users using the `UserSeeder.seed(10)` method.
   - Calls the `seed_cleaner` command to seed additional data.

4. **Seed Cleaner Data**:
   The `seed_cleaner` command is used to populate the database with cleaner data. It takes data from an Excel file and seeds it into the database. The path to the Excel file is specified in the `.env` file under the `CLEANER_FILE` variable:
   ```properties
   CLEANER_FILE="/path/to/cleaners.xlsx"
   ```
   Ensure the Excel file is properly formatted and located at the specified path. This command is automatically called by `seed_db`, but you can also run it independently:
   ```bash
   python manage.py seed_cleaner
   ```

5. **Reset the Database**:
   If you need to reset the database, use the `reset_db` command:
   ```bash
   python manage.py reset_db
   ```
   After resetting, reapply migrations and seed the database:
   ```bash
   python manage.py migrate
   python manage.py seed_db
   ```

   > **Note**: You do not need to run `makemigrations` after `reset_db` unless you have made changes to your models.

6. **Example Output**:
   When you run the `seed_db` command, you should see output like this:
   ```
   Seeding Database...
   Superuser created successfully.
   10 sample users seeded successfully.
   Seeding Cleaners...
   Cleaners seeded successfully.
   Database seeded successfully.
   ```

---

## Setting Up Environment Variables

### Backend `.env` Example

The backend requires a `.env` file for configuration. Below is a sample `.env` file:

```properties
# Secret key for Django
SECRET_KEY=django-insecure-k%6g&zrmq8*k&$0zaga=okin2=*zfz*_*l1i%#l13%+%0xc#u-

# PostgreSQL database configuration
POSTGRES_DB=autoclean
POSTGRES_USER=root
POSTGRES_PASSWORD=password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Celery configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Path to the Excel file for seeding cleaner data
CLEANER_FILE=/path/to/cleaners.xlsx
```

> **Note**: Update the `CLEANER_FILE` path to the location of your Excel file for seeding cleaner data.

---

### Frontend `.env.development` Example

The frontend requires a `.env.development` file for development. Below is a sample `.env.development` file:

```bash
# Base URL for the backend API
VITE_API_BASE_URL=http://localhost:8000
```

> **Note**: Replace `http://localhost:8000` with the actual backend URL if running on a different host or port.

---

### Frontend `.env.production` Example

For production, the frontend requires a `.env.production` file. Below is a sample `.env.production` file:

```bash
# Base URL for the backend API
VITE_API_BASE_URL=http://your-production-backend-url
```

> **Note**: Replace `http://your-production-backend-url` with the actual backend URL for your production environment.

---

These examples should help first-time users set up their environment variables correctly for both the frontend and backend.

---

## Technologies Used

### Backend
- Django
- Celery
- Redis (as a message broker for Celery)
- PostgreSQL

### Frontend
- React
- Redux
- Tailwind CSS
