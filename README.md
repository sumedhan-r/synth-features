# Synth Features

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Technologies & References](#technologies--references)
  - [Tech Stack](#tech-stack)
  - [Frameworks](#frameworks)
  - [References](#references)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Local Deployment](#local-deployment)
  - [Option 1: Docker (Recommended)](#option-1-docker-recommended)
  - [Option 2: Native Python](#option-2-native-python)
  - [Configuration](#configuration)
- [Testing](#testing)

## Introduction

A collection of tools and prototypical features for a Synthesizer Product. This repository serves as an experimental platform for exploring sound synthesis frameworks and implementing synthesizer features with a production-ready API architecture.

## Features

- **String Instrument Synthesis**: Simulate plucked string instruments (guitar, ukulele) using the Karplus-Strong algorithm
- **Chorus Generation**: Create strumming patterns with customizable chord progressions, stroke patterns, and intervals
- **Streaming Audio**: Real-time audio streaming via FastAPI endpoints
- **Configurable Presets**: Built-in instrument presets with support for custom tuning, vibration, and damping parameters
- **Platform-Agnostic Deployment**: Run locally or deploy to cloud platforms (Azure, AWS, GCP) with database flexibility

## Technologies & References

### Tech Stack

- **Python**: 3.11
- **Web Framework**: FastAPI, Uvicorn
- **Audio Processing**: NumPy, SciPy, Pedalboard
- **Data Validation**: Pydantic
- **Database Support**: SQLAlchemy with PostgreSQL, MySQL, or SQLite
- **Telemetry**: OpenTelemetry (distributed tracing, metrics)
- **Containerization**: Docker, Docker Compose

### Frameworks

- **pywdf**: A framework for modeling Virtual Analog circuits used in analog music and sound synthesis. [Paper Link](https://www.dafx.de/paper-archive/2023/DAFx23_paper_23.pdf)

### References

- **String Synthesis Implementation**: The Karplus-Strong algorithm and plucked string instrument synthesis in this project are refactored and adapted from [Real Python's Guitar Synthesizer Tutorial](https://realpython.com/python-guitar-synthesizer/)

## Getting Started

### Prerequisites

- **Python**: 3.11.x
- **Poetry**: 2.1.3 or higher (for dependency management)
- **Docker & Docker Compose** (optional, for containerized deployment)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd synth-features
   ```

2. **Install dependencies using Poetry**

   ```bash
   poetry install
   ```

3. **Activate the virtual environment**
   ```bash
   poetry shell
   ```

## Local Deployment

**Run the interactive deployment script:**

```bash
bash scripts/run-local-deploy.sh
```

The script provides options for:

- Database selection (PostgreSQL, MySQL, SQLite, or none)
- Custom database credentials
- Docker Compose actions (up, down, restart, logs)

The API will be available at `http://localhost:8100`

**Configuration**: Customize instrument presets and platform settings in `configs/local.config.yaml`

## Testing

**Run unit tests:**

```bash
bash scripts/run-unit-test.sh
```

**Run integration tests:**

```bash
bash scripts/run-integration-test.sh
```
