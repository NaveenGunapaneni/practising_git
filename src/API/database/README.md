# GeoPulse Database Setup

This folder contains the Docker Compose configuration and SQL scripts to set up the PostgreSQL database for the GeoPulse API.

## Quick Start

1. **Start the database:**
   ```bash
   cd database
   docker-compose up -d
   ```

2. **Check if the database is running:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs postgres
   ```

## Database Details

- **Container Name:** `geopulse_postgres`
- **Database:** `geopulse_db`
- **User:** `geopulse_user`
- **Password:** `password123`
- **Port:** `5432`

## Tables Created

### users
- `user_id` (Primary Key)
- `organization_name`
- `user_name`
- `contact_phone`
- `email` (Unique)
- `password_hash`
- `logo_path`
- `file_count` (Auto-updated via trigger)
- `created_at`
- `updated_at`

### files
- `file_id` (Primary Key)
- `user_id` (Foreign Key to users)
- `upload_date`
- `filename`
- `original_filename`
- `line_count`
- `storage_location`
- `input_location`
- `processed_flag`
- `engagement_name`
- `browser_ip`
- `browser_location`
- `processing_time_seconds`
- `file_size_mb`
- `dates` (JSONB)
- `error_message`
- `created_at`
- `updated_at`

## Management Commands

### Stop the database:
```bash
docker-compose down
```

### Stop and remove all data:
```bash
docker-compose down -v
```

### Connect to the database:
```bash
docker-compose exec postgres psql -U geopulse_user -d geopulse_db
```

### Backup database:
```bash
docker-compose exec postgres pg_dump -U geopulse_user geopulse_db > backup.sql
```

### Restore database:
```bash
docker-compose exec -T postgres psql -U geopulse_user geopulse_db < backup.sql
```

## pgAdmin Web Interface

Access pgAdmin at: **http://localhost:8080**

**Login Credentials:**
- Email: `admin@geopulse.com`
- Password: `admin123`

**To connect to your database in pgAdmin:**
1. Right-click "Servers" → "Register" → "Server"
2. **General Tab:**
   - Name: `GeoPulse DB`
3. **Connection Tab:**
   - Host: `postgres` (container name)
   - Port: `5432`
   - Database: `geopulse_db`
   - Username: `geopulse_user`
   - Password: `password123`

## Command Line Access

Connect directly via command line:
```bash
docker-compose exec postgres psql -U geopulse_user -d geopulse_db
```

## Connection String

The connection string for your application should be:
```
postgresql+asyncpg://geopulse_user:password123@localhost:5432/geopulse_db
```

This matches the `DATABASE_URL` in your `.env` file.