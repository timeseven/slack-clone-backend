# Slack Clone Backend with FastAPI

This is a modular, real-time backend built with FastAPI. It supports messaging, notifications, workspace management, and async job handling with ARQ. Designed with scalability, modularity, and modern API practices in mind.

---

## 🚀 Features

- ⚡ **Real-Time Messaging with Socket.IO**
  - Messages sent via REST API are broadcast via Socket.IO
  - Users join 3 types of rooms: `user`, `workspace`, and `channel`
  - Online users receive real-time updates; offline users are handled asynchronously

- 🧠 **Asynchronous Task Handling with ARQ**
  - Email tasks: registration verification, password reset, workspace invites
  - Offline notifications for users with unread messages

- 🔐 **Secure Authentication with Dual Token Strategy**
  - Access Token (short-lived) + Refresh Token (long-lived) stored in HTTPOnly cookies
  - Refresh tokens are stored in Redis, enabling token invalidation (e.g., logout, multi-device(maximum 3 devices))
  - When Redis record is deleted, user must re-authenticate after access token expiry

- 📦 **Modular Architecture**
  - Clean separation of layers: `routes` / `services` / `repos` / `interface`
  - `routes`: define HTTP endpoints using FastAPI, calling corresponding services.
  - `repos`: per-module DB operations using SQLalchemy Core
  - `services`: contain core business logic for the module, used by both its own routes and other modules via interface
  - `interface`: declare service-level contracts exposed to other modules, allowing decoupled

- ✅ **Unified Response & Exception Handling**
  - All API responses and errors follow a consistent format


## ⚙️ Getting Started

### 1. Install Docker and Docker Compose
Make sure Docker and Docker Compose are installed. Then start Redis and the database using the provided docker-compose.yml.
```
docker-compose up -d
```

### 2. Set up environment variables
Rename .env.dev to .env and fill in the required configuration variables.

### 3. Install uv and just
Install uv for Python depencency management and just as a command runner.

### 4. Install depencencies and run the project
Use uv to install dependencies
```
uv venv
uv sync
```
Then user just to run the project
```
just migrate  # Migrate db
just run      # Start FastAPI server
just arq      # Start ARQ worker
```