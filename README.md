# Host Management System

A comprehensive Genropy/Erpy package for managing accommodation facilities, guest tracking, and tourist tax reporting.

## Maintainer

- **Davide Paci** (@dgpaci)

## Overview

The Host Management System is designed for accommodation facilities (hotels, B&Bs, vacation rentals) to manage:

- Facility information and types
- Guest registry with document tracking
- Stay records with automatic night calculation
- Tourist tax calculation and tracking
- Police report generation (Italian ISTAT format)

## Features

### 1. Facility Management
- Register multiple accommodation facilities
- Link facilities to owner/manager registry (via `erpyready.anagrafica`)
- Categorize facilities by type (hotel, B&B, apartment, etc.)

### 2. Guest Registry
- Complete guest information linked to `erpyready.anagrafica`
- Document tracking (passport, identity card) for group leaders
- Personal data: name, surname, birth date, birthplace, citizenship
- Automatic linkage to existing registry records

### 3. Stay Tracking
- Record check-in and check-out dates
- Automatic calculation of number of nights
- Group management with designated group leader
- Multiple guests per stay with individual tax rates

### 4. Tourist Tax Management
- Configurable tax rates with exemption codes
- Italian tourist tax compliance (códigos de exención)
- Automatic tax calculation based on:
  - Number of nights
  - Guest age (exemptions for children under 12)
  - Specific exemption categories
- Individual tax tracking per guest

### 5. Police Report Export
- Generate TXT files for Italian police (Questura) reporting
- 178-character fixed-width format per guest
- ISTAT code integration for municipalities and countries
- Compliance with official Italian accommodation reporting requirements

## Database Schema

### Lookup Tables

#### `facility_type` (Lookup)
Types of accommodation facilities
- `id` (PK)
- `code` - Type code
- `description` - Type description

#### `guest_type` (Lookup)
Guest type classification (Tipo Alloggiato)
- `id` (PK)
- `code` - Guest type code
- `description` - Guest type description
- `is_leader` - **Calculated field** (TRUE if code is '17' or '18')

**Official Codes**:
- `16`: OSPITE SINGOLO (Single guest)
- `17`: CAPO FAMIGLIA (Family head) - **Leader**
- `18`: CAPO GRUPPO (Group head) - **Leader**
- `19`: FAMILIARE (Family member)
- `20`: MEMBRO GRUPPO (Group member)

#### `document_type` (Lookup)
Types of identification documents (96 official Italian codes)
- `id` (PK)
- `code` - Document code (e.g., "IDENT", "PASOR")
- `description` - Document description (e.g., "CARTA DI IDENTITA'", "PASSAPORTO ORDINARIO")

**Standard Codes** (partial list):
- `IDENT`: CARTA DI IDENTITA'
- `IDELE`: CARTA IDENTITA' ELETTRONICA
- `PASOR`: PASSAPORTO ORDINARIO
- `PATEN`: PATENTE DI GUIDA
- (See initial_data.sql for complete list of 96 document types)

#### `tourist_tax` (Lookup)
Tourist tax rates and exemptions
- `id` (PK)
- `code` - Tax code (e.g., "0000000001" to "0000000009")
- `description` - Tax description/exemption reason
- `amount` - Tax amount per night (EUR)

**Standard Codes** (from Italian tourist tax regulations):
- `0000000001`: Exemption for minors under 12 years
- `0000000002`: Exemption for residents
- `0000000003`: Exemption for tour guides (groups of 25+)
- `0000000004`: Exemption for facility staff
- `0000000005`: **NO EXEMPTION** (standard rate)
- `0000000006`: Exemption for non-self-sufficient persons with medical certificate
- `0000000007`: Exemption for Civil Protection volunteers
- `0000000008`: Exemption for police and military personnel on duty
- `0000000009`: Exemption for guests with free accommodation

### Main Tables

#### `facility`
Accommodation facilities registry
- `id` (PK)
- `anagrafica_id` (FK to `erpyready.anagrafica`) - Owner/Manager
- `name` - Facility name
- `facility_type_id` (FK to `facility_type`)

#### `stay`
Accommodation stays
- `id` (PK)
- `facility_id` (FK to `facility`)
- `check_in_date` - Check-in date
- `check_out_date` - Check-out date
- `arrival_time` - Arrival time (optional)
- `flight_number` - Flight number (optional)
- `safe_code` - Safe code for apartment access (optional)
- `nights` - **Calculated field** (check_out_date - check_in_date)

**Calculated Fields**:
- `nights`: Automatically calculated from date difference
- `stay_caption`: Display caption combining facility name and dates
- `group_leader_name`: Calculated from guests with leader role

**Validation**:
- Check-out date must be after check-in date

#### `guest`
Guest records for stays
- `id` (PK)
- `stay_id` (FK to `stay`) - Stay reference
- `anagrafica_id` (FK to `erpyready.anagrafica`) - Personal data
- `guest_type_id` (FK to `guest_type`) - Guest type (single, family head, group head, member)
- `tourist_tax_id` (FK to `tourist_tax`) - Tax rate or exemption
- `document_type_id` (FK to `document_type`) - Document type
- `document_number` - Document number
- `document_issued_by` - Issuing authority/place
- `document_issue_date` - Issue date
- `document_expiry_date` - Expiry date
- `tax_amount` - **Calculated field** (nights × tax rate per municipality)

**Business Logic**:
- Each guest belongs to one stay (one-to-many relationship)
- Document fields are required only for group leaders (guest types 17, 18)
- If the same person returns, create a new guest record referencing the same anagrafica
- Each stay should have at least one group leader (guest_type code '17' or '18')
- Tax amount is automatically calculated via trigger based on:
  - Number of nights from stay
  - Tax rate from tourist_tax for the facility's municipality
  - Exemptions (tax_rate = 0)

## Installation

1. Copy the `host` package to your Erpy packages directory:
   ```bash
   cp -r host /path/to/erpy_projects/your_instance/packages/
   ```

2. The package requires `erpyready` for the anagrafica (registry) integration

3. Restart your Genropy instance to load the package

4. The package will automatically create the `host` SQL schema and tables

## Usage

### Menu Structure

**Host Management**
- Master Data
  - Facilities
  - Facility Types
  - Guests
  - Guest Types
  - Document Types
  - Tourist Tax Rates
- Operations
  - Stays

### Typical Workflow

1. **Setup Master Data**
   - Guest types are pre-loaded (5 official codes)
   - Document types are pre-loaded (96 official codes)
   - Create facility types (Hotel, B&B, Apartment, etc.)
   - Configure tourist tax rates with exemption codes

2. **Register Facilities**
   - Link to existing anagrafica record (owner/manager)
   - Specify facility name and type

3. **Create Stays**
   - Select facility
   - Enter check-in and check-out dates (nights calculated automatically)
   - Optional: arrival time, flight number, safe code
   - Add guests to the stay:
     - Link to existing anagrafica or create new inline
     - Select guest_type for each guest (16=single, 17=family head, 18=group head, 19=family member, 20=group member)
     - At least one guest must be a leader (type 17 or 18)
     - For group leaders: enter document information
     - Assign tourist tax rate for each guest
     - Tax amount calculated automatically based on nights and facility municipality

4. **Export Police Report**
   - From the stay form, click "Export TXT for Police"
   - Generated file contains 178-character lines per guest
   - Format complies with Italian police reporting requirements

## Police Report Format

The export generates a fixed-width text file (178 characters per guest) with the following fields:

| Field | Length | Type | Description |
|-------|--------|------|-------------|
| Guest Type | 2 | N | 16=single, 17=family head, 18=group head, 19=family member, 20=group member |
| Arrival Date | 10 | AN | Format: gg/mm/aaaa |
| Days of Stay | 2 | N | Maximum 30 days |
| Surname | 50 | A | Guest surname |
| Name | 30 | A | Guest first name |
| Gender | 1 | N | 1=Male, 2=Female |
| Birth Date | 10 | AN | Format: gg/mm/aaaa |
| Birth Municipality | 9 | N | ISTAT code |
| Birth Province | 2 | A | Province code |
| Birth Country | 9 | N | Country code |
| Citizenship | 9 | N | Country code |
| Document Type | 5 | AN | Document type code |
| Document Number | 20 | AN | Document number |
| Document Issue Place | 9 | N | Municipality ISTAT code |
| Tourist Tax Code | 10 | N | Tax/exemption code (optional) |

**Legend**:
- N = Numeric (padded left with zeros)
- A = Alphabetic (padded right with spaces)
- AN = Alphanumeric (padded right with spaces)

## Integration with Erpy Base

The package integrates with `erpyready` for:

### Anagrafica (Registry)
Guest and facility owner data is stored in `erpyready.anagrafica` which includes:
- `cognome` (surname)
- `nome` (name)
- `ragione_sociale` (full name)
- `sesso` (gender): M/F
- `data_nascita` (birth date)
- `luogo_nascita`, `comune_nascita`, `provincia_nascita`, `stato_nascita` (birth place)
- `cittadinanza` (citizenship)
- Address, phone, email, etc.

### GLBL Tables
- `glbl.comune`: Italian municipalities with ISTAT codes
- `glbl.nazione`: Countries with codes for police reporting

## Development

### File Structure

```
host/
├── main.py                          # Package configuration
├── menu.py                          # Menu structure
├── model/                           # Database models
│   ├── facility.py
│   ├── facility_type.py
│   ├── guest.py
│   ├── guest_type.py
│   ├── document_type.py
│   ├── stay.py
│   ├── stay_guest.py
│   └── tourist_tax.py
├── resources/
│   ├── services/
│   │   └── police_export.py        # Police report export service
│   └── tables/                      # Table handlers (UI)
│       ├── facility/
│       │   └── th_facility.py
│       ├── facility_type/
│       │   └── th_facility_type.py
│       ├── guest/
│       │   └── th_guest.py
│       ├── guest_type/
│       │   └── th_guest_type.py
│       ├── document_type/
│       │   └── th_document_type.py
│       ├── stay/
│       │   └── th_stay.py
│       ├── stay_guest/
│       │   └── th_stay_guest.py
│       └── tourist_tax/
│           └── th_tourist_tax.py
└── README.md
```

### Key Design Decisions

1. **Anagrafica Integration**: Personal data stored in centralized registry to avoid duplication
2. **Guest-Stay Relationship**: Each guest belongs to one stay (one-to-many). If the same person returns, create a new guest record referencing the same anagrafica
3. **Guest Type System**: Uses official Italian codes (16-20) to classify guests with mandatory sysRecord
4. **Group Leader Model**: Only group leaders (types 17, 18) require document tracking
5. **Calculated Fields**: Nights and tax amounts calculated automatically via triggers
6. **Tourist Tax Management**: Tax rates configured per municipality using bag structure; 9 official exemption codes as mandatory sysRecord
7. **Stay-centric View**: UI shows stays with group leader, not individual guests
8. **Lookup Tables as Code-based**: All lookup tables use `code` as primary key instead of auto-generated id
9. **Italian Compliance**:
   - 5 official guest types (Tipo Alloggiato) - mandatory sysRecord
   - 96 official document types
   - 9 official tourist tax exemption codes - mandatory sysRecord
   - Police export follows official ISTAT format (178 chars)

## API / Services

### PoliceExportService

```python
from host.resources.services.police_export import PoliceExportService

service = PoliceExportService(db)
content = service.export_stay(stay_id)
```

**Methods**:
- `export_stay(stay_id)`: Export all guests for a stay
- Returns string with 178-character lines (one per guest)

**Usage**:
```python
# Export to string
content = service.export_stay(stay_id)

# Export to file
from host.resources.services.police_export import export_stay_to_file
file_path = export_stay_to_file(db, stay_id, '/path/to/output.txt')
```

## Requirements

- Genropy framework
- Erpy base package (`erpyready`)
- PostgreSQL or compatible database
- Python 3.7+

## License

Proprietary - Softwell S.r.l.

## Support

For issues, questions, or contributions, contact:
- Davide Paci (@dgpaci)

## Version History

- **2.0.0** (2026-01-26): Major refactoring
  - Simplified data model: guest belongs to one stay (one-to-many instead of many-to-many)
  - Integration with `er_core:erpy_ready` instead of `erpy:erpy_base`
  - All lookup tables use `code` as primary key
  - Mandatory sysRecord for guest types and tourist tax codes
  - Improved tax calculation with municipality-specific rates via bag structure

- **1.0.0** (2026-01-23): Initial release
  - Complete facility and guest management
  - Stay tracking with automatic calculations
  - Tourist tax management
  - Police report export (Italian format)
