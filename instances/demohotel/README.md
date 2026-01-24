# Demo Hotel Instance

Test instance for the Host Management System package.

## Packages Included

- **sys** - System package
- **adm** - Administration package
- **glbl** - Global data (countries, municipalities, etc.)
- **host** - Host Management System (this package)

## Database Setup

### 1. Create PostgreSQL Database

```bash
createdb -U postgres demohotel
```

Or via psql:

```sql
CREATE DATABASE demohotel;
```

### 2. Initialize Database Schema

Start the Genropy instance for the first time to create all tables:

```bash
gnrwsgi demohotel
```

Genropy will automatically create all table structures for the included packages.

### 3. Load Initial Data

After the database schema is created, load the lookup table data:

```bash
psql -U postgres -d demohotel -f ../../initial_data.sql
```

This will populate:
- Guest types (5 official Italian codes)
- Document types (96 official Italian codes)
- Facility types (7 examples)
- Tourist tax rates (9 Italian regulation codes)

## Starting the Instance

### Development Mode

```bash
gnrwsgi demohotel
```

The instance will be available at: **http://localhost:8090**

### Configuration

The instance is configured for development with:
- **Port**: 8090
- **Debug mode**: Enabled
- **Auto-reload**: Enabled
- **Default language**: Italian
- **Available languages**: Italian, English

## Default Credentials

Use the default Genropy admin credentials created during first setup.

## Database Configuration

Edit `instanceconfig.xml` to modify database connection settings:
- **Database name**: demohotel
- **Host**: localhost
- **Port**: 5432
- **User**: postgres
- **Password**: (empty by default)

## Testing Workflow

1. Create a facility (specify name, type, owner, municipality)
2. Configure tourist tax rates per municipality (in Tourist Tax Rates menu)
3. Create guest records with personal and document information
4. Create a stay (check-in/check-out dates, arrival info)
5. Add guests to the stay with appropriate guest types and tax rates
6. Generate police report export (TXT format)

## Notes

- The instance uses PostgreSQL as the database backend
- All Italian regulatory compliance features are enabled
- ISTAT codes for municipalities and countries are provided by the glbl package
