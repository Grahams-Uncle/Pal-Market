# Pal-Market

**Pal-Market** is a full-stack, Palworld-themed auction marketplace inspired by eBay. Pals are the merchandise: users can list Pals for auction and place bids on listings.

**Repository:** [Grahams-Uncle/Pal-Market](https://github.com/Grahams-Uncle/Pal-Market)

## Overview

Pal-Market applies familiar online-auction concepts to a game-inspired setting. The project combines a Flask web application with a PostgreSQL database to support an auction marketplace centered on Pals from *Palworld*.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** PostgreSQL, SQL
- **Environment and dependencies:** Poetry

## Getting Started

The original project setup assumes the course-provided container environment. Running it on another machine may require additional configuration.

### Installation

```bash
git clone https://github.com/Grahams-Uncle/Pal-Market.git
cd Pal-Market
./install.sh
```

The installation script sets up the project environment and initializes the PostgreSQL database named `amazon` (a name retained from the original course starter code).

### Run the Application

```bash
poetry shell
flask run
```

In the original local-container setup, open **http://localhost:8080/**. The URL may differ depending on your Flask and container configuration.

### Database Setup

To reset and initialize the database, stop the Flask server and any active PostgreSQL sessions, then run:

```bash
db/setup.sh
```

To inspect the database directly:

```bash
psql amazon
```

Database schema and seed data are maintained under `db/`, including `db/create.sql` and `db/load.sql`.

## Repository Structure

```text
Pal-Market/
├── app/                    # Flask application
├── db/                     # Database schema and setup files
├── milestone_submissions/  # Course project milestones
├── install.sh              # Environment installation script
├── pyproject.toml          # Python project configuration
├── poetry.lock             # Locked dependencies
└── README.md
```

## Configuration and Security

The original project uses a local `.flaskenv` file for environment-specific settings and secrets. **Do not commit credentials or secret keys to version control.**

## Acknowledgments

Developed as a project based on the Duke CompSci 316/516 course starter application, originally created by Rickard Stureborg and Yihao Hu and subsequently maintained by course staff.

## License

This repository includes an [MIT license](LICENSE).
