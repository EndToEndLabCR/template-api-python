# Template API Project

This project serves as a template for building scalable and maintainable API services. It provides a structured foundation for developers to kickstart their projects with essential features and configurations. The primary purpose is to simplify the development process and ensure best practices are followed. Intended users include developers and teams working on API-based applications.

## 📑 Table of Contents

- [Template API Project](#template-api-project)
  - [📑 Table of Contents](#-table-of-contents)
  - [✨ Features](#-features)
  - [🛠️ Technologies Used](#️-technologies-used)
  - [🚀 Getting Started](#-getting-started)
    - [⚙️ Prerequisites](#️-prerequisites)
    - [💾 Installation](#-installation)
    - [📝 Configuration](#-configuration)
    - [Pip](#pip)
    - [🏃 Running the App](#-running-the-app)
      - [🐳 Running with Docker](#-running-with-docker)
      - [🖥️ Running with PyCharm](#️-running-with-pycharm)
  - [🗄️ Database Management](#️-database-management)
    - [Initial Setup](#initial-setup)
    - [Creating Migrations](#creating-migrations)
    - [Running Migrations](#running-migrations)
  - [🤝 Contributing](#-contributing)

## ✨ Features

- User authentication and authorization
- RESTful API design
- Modular and scalable architecture
- Environment-based configurations
- Logging and error handling
- Unit and integration testing

[⬆️ Back to Top](#template-api-project)

## 🛠️ Technologies Used

- [Python](https://www.python.org/) - Core programming language
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework for building APIs
- [PostgreSQL](https://www.postgresql.org/) - Relational database
- [Docker](https://www.docker.com/) - Containerization platform
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation and settings management

[⬆️ Back to Top](#template-api-project)

## 🚀 Getting Started

### ⚙️ Prerequisites

- Python 3.9+
- Docker (optional, for containerized deployment)
- PostgreSQL (if not using Docker)

### 💾 Installation

```sh
# Clone the repository
git clone https://github.com/your-username/template-api-python.git
cd your-repo

```

[⬆️ Back to Top](#template-api-project)

### 📝 Configuration

The [.env.example](.env.example) file under root folder shows which variables should be included in your local .env file.
Ask a team member for the specific values to complete this step.

- .env

These files define runtime variables such as API endpoints, authentication settings, and environment-specific flags.

[⬆️ Back to Top](#template-api-project)

### Pip

- Create the pip environment:

  ```sh
   python -m venv venv
  ```

- Activate the pip environment:

  ```sh
   source venv/bin/activate
  ```

- In case you need to update pip:

  ```sh
    pip install --upgrade pip
  ```

- Install the project's core dependencies:

  ```sh
   pip install -r requirements.txt
  ```

- Deactivate virtual environment:

  ```sh
  deactivate
  ```

### 🏃 Running the App

#### 🐳 Running with Docker

Ensure Docker and Docker Compose are installed on your system.

1. **Clean up existing containers and caches:**

   To avoid issues caused by cached images, volumes, or orphaned containers, run the following command:

   ```sh
   docker-compose down --rmi all --volumes --remove-orphans
   ```

2. **Build and start the application:**

   Build the Docker images and run the containers in detached mode by executing:

   ```sh
   docker-compose up --build -d
   ```

3. **Access the app:**

   Once the containers are up, you can access the app's Swagger UI at:  
   `http://localhost:8080/docs`

   [Docker local run example](docs/running-app/docker-run.png)

---

#### 🖥️ Running with PyCharm

If you prefer running the app directly from the PyCharm IDE, follow these steps:

1. **Set up the Python interpreter:**

   - Navigate to PyCharm's settings (`File -> Settings -> Project -> Python Interpreter`).
   - Select the Python interpreter located at:  
     `your-repo/venv/bin/python`

2. **Configure the working directory:**

   - In your run configuration, set the **working directory** to:  
     `your-repo`

3. **Set up the module and script parameters:**

   - **Module:** `uvicorn`
   - **Script parameters:**  
     `src.main:app --reload`

4. **Run the application:**

   - Save the run configuration and start the app.

5. **Access the app:**

   The app will be available at:  
   `http://localhost:8000/docs`

   [PyCharm local run settings example](docs/running-app/pycharm-run-setup.png)

---

## 🗄️ Database Management

### Initial Setup

```bash
# Initialize Alembic (if not already done)
alembic init alembic

# Configure Alembic to use your database URL
# Add this line to alembic/env.py (line 13):
config.set_main_option("sqlalchemy.url", get_postgres_database_url())
```

### Creating Migrations

```bash
# Create a new migration after model changes
alembic revision --autogenerate -m "Description of changes"
```

### Running Migrations

```bash
# Apply all pending migrations
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Downgrade one version
alembic downgrade -1

# View migration history
alembic history
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -am 'Add feature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Open a pull request

---

[⬆️ Back to Top](#template-api-project)

_Built with ❤️ by [EndToEndLabCR](https://github.com/EndToEndLabCR)_
