# Demo Hotel Instance

Test instance for the Host Management System package.

## Structure

```
demohotel/
├── config/
│   └── instanceconfig.xml    # Instance configuration
├── root.py                     # WSGI application entry point
└── site/                       # Site data directory (auto-created)
```

## Packages Included

- **gnrcore:sys** - Genropy System package
- **gnrcore:adm** - Genropy Administration package
- **gnr_it:glbl** - Italian Global data (municipalities, countries, etc.)
- **er_coerpyreadyeady** - Erpy Ready package (anagrafica, registry)
- **host:host** - Host Management System (this package)

## Database Setup

### 1. Create PostgreSQL Database

```bash
createdb -U postgres demohotel
```

Or via psql:

```sql
CREATE DATABASE demohotel;
```

### 2. Run Database Migration

Initialize the database schema:

```bash
cd /Users/dgpaci/sviluppo/erpy_projects/host
gnr db migrate demohotel
```

This will create all tables for the included packages.

### 3. Load Initial Data

After migration, load the lookup table data:

```bash
psql -U postgres -d demohotel -f initial_data.sql
```

This will populate:
- Guest types (5 official Italian codes)
- Document types (96 official Italian codes)
- Facility types (7 examples)
- Tourist tax rates (9 Italian regulation codes)

## Starting the Instance

### Development Mode

```bash
cd /Users/dgpaci/sviluppo/erpy_projects/host/instances/demohotel
python root.py
```

Or using gnrwsgi:

```bash
gnrwsgi demohotel
```

The instance will be available at: **http://localhost:8090**

## Configuration

The instance is configured in `config/instanceconfig.xml`:
- **Database**: demohotel (PostgreSQL)
- **Port**: 8090
- **Debug mode**: Enabled
- **Main package**: host
- **Authentication**: Standard Genropy authentication via adm package

## Default Credentials

After first migration, create an admin user via the adm package interface.

## Testing Workflow

1. **Create a facility** (specify name, type, owner, municipality)
2. **Configure tourist tax rates** per municipality (Tourist Tax Rates menu)
   - Select each tax code
   - Add municipality in the grid
   - Set the amount (EUR per night)
3. **Create guest records** with personal and document information
4. **Create a stay**:
   - Check-in/check-out dates
   - Arrival time and flight number (optional)
   - Safe code for apartment access (optional)
5. **Add guests to the stay** with:
   - Guest type (single, family head, group head, member)
   - Tax rate/exemption
   - Tax amount calculated automatically
6. **Generate police report export** (TXT format, 178 characters per line)

## Notes

- The instance uses PostgreSQL as the database backend
- All Italian regulatory compliance features are enabled
- ISTAT codes for municipalities and countries are provided by gnr_it:glbl package
- Tourist tax amounts are managed per municipality using bag structure
