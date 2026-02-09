# Host Package - Development Context

## Project Overview

The Host Management System is a Genropy/Erpy package for managing accommodation facilities (hotels, B&Bs, vacation rentals) with Italian regulatory compliance for guest tracking, tourist tax calculation, and police reporting.

### Key Features
- Facility and guest registry management
- Stay tracking with automatic night calculation
- Tourist tax calculation with exemption codes
- Police report export (Italian ISTAT format - 178 characters)
- Integration with Alloggiati Web SOAP webservice (planned)
- Ross1000 integration (planned)
- Online check-in system with signed links (planned)

### Repository Structure

```
/Users/dgpaci/sviluppo/erpy_projects/host/
├── README.md              # User documentation
├── CONTEXT.md            # This file - development context
├── initial_data.sql      # Lookup table data (guest types, documents, etc.)
├── .gitignore
└── packages/
    └── host/             # Main Genropy package
        ├── main.py       # Package configuration
        ├── menu.py       # Menu structure
        ├── model/        # Database models (8 tables)
        ├── resources/
        │   ├── services/     # Business logic services
        │   └── tables/       # UI table handlers (th_*.py)
        └── webpages/         # Web pages
            └── index.py      # Main page (required for mainpackage)
```

## Database Architecture

### Schema: `host`

All tables use the `host` SQL schema. Integration with `erpyready` schema for anagrafica (registry) and `glbl` schema for ISTAT codes.

### Core Tables

#### 1. `facility_type` (Lookup)
Types of accommodation facilities.
- `id` (PK)
- `code` - Unique type code (e.g., "HOTEL", "BB")
- `description` - Type description
- Uses `sysFields()` for audit fields

**Example data**: HOTEL, BB (Bed & Breakfast), APART (Apartment), AGRITU (Agriturismo), HOSTEL, VILLA, CAMPING

#### 2. `guest_type` (Lookup)
Official Italian guest type classification (Tipo Alloggiato).
- `id` (PK)
- `code` - Official 2-digit code (16-20)
- `description` - Type description
- `is_leader` - **Calculated field** (TRUE if code is '17' or '18')

**Official codes** (from tipo_alloggiato.csv):
```
16 - OSPITE SINGOLO (Single guest)
17 - CAPO FAMIGLIA (Family head) - LEADER
18 - CAPO GRUPPO (Group head) - LEADER
19 - FAMILIARE (Family member)
20 - MEMBRO GRUPPO (Group member)
```

**Architectural note**: Originally designed with boolean `is_group_leader` flag, refactored to use FK `guest_type_id` to comply with official Italian codes.

#### 3. `document_type` (Lookup)
Official Italian identification document types (96 codes).
- `id` (PK)
- `code` - Official 5-character code (e.g., "IDENT", "PASOR")
- `description` - Document description

**Common codes** (from documenti.csv):
```
IDENT  - CARTA DI IDENTITA'
IDELE  - CARTA IDENTITA' ELETTRONICA
PASOR  - PASSAPORTO ORDINARIO
PATEN  - PATENTE DI GUIDA
PATNA  - PATENTE NAUTICA
CIDIP  - CARTA ID. DIPLOMATICA
PASSE  - PASSAPORTO DI SERVIZIO
```
Total: 96 official document types in initial_data.sql

#### 4. `tourist_tax` (Lookup)
Tourist tax rates and exemption codes.
- `id` (PK)
- `code` - 10-digit tax code (e.g., "0000000001")
- `description` - Tax description or exemption reason
- `amount` - Tax amount per night (EUR, can be 0.00 for exemptions)

**Standard codes** (from codici-tariffe-imposta-soggiorno.csv):
```
0000000001 - Exemption for minors under 12 years
0000000002 - Exemption for residents
0000000003 - Exemption for tour guides (groups of 25+)
0000000004 - Exemption for facility staff
0000000005 - NO EXEMPTION (standard rate, e.g., €2.50)
0000000006 - Exemption for non-self-sufficient persons with medical certificate
0000000007 - Exemption for Civil Protection volunteers
0000000008 - Exemption for police and military personnel on duty
0000000009 - Exemption for guests with free accommodation
```

#### 5. `facility`
Accommodation facilities registry.
- `id` (PK)
- `anagrafica_id` (FK to `erpyready.anagrafica`) - Owner/Manager
- `name` - Facility name
- `facility_type_id` (FK to `facility_type`)

**Relations**:
- Many facilities per anagrafica (owner can have multiple facilities)
- One facility_type per facility

#### 6. `guest`
Guest records for accommodation stays.
- `id` (PK)
- `stay_id` (FK to `stay`) - Stay reference
- `anagrafica_id` (FK to `erpyready.anagrafica`) - Personal data
- `guest_type_id` (FK to `guest_type`) - Guest type (single, family head, group head, member)
- `tourist_tax_id` (FK to `tourist_tax`) - Tax rate or exemption
- `document_type_id` (FK to `document_type`) - Document type
- `document_number` - Document number
- `document_issued_by` - Issuing authority/place
- `document_issue_date` - Issue date (D)
- `document_expiry_date` - Expiry date (D)
- `tax_amount` - **Calculated field** (nights × tax_rate per municipality)

**Business rules**:
- Each guest belongs to one stay
- Document fields are **required only for group leaders** (guest types 17, 18)
- Personal data (name, surname, birth date, etc.) stored in `erpyready.anagrafica`
- If the same person returns, create a new guest record referencing the same anagrafica
- Tax amount auto-calculated based on stay nights and tax rate for facility's municipality

**Alias columns** (for UI display):
- `full_name` - From @anagrafica_id.ragione_sociale
- `surname` - From @anagrafica_id.cognome
- `name` - From @anagrafica_id.nome
- `birth_date` - From @anagrafica_id.data_nascita
- `citizenship` - From @anagrafica_id.cittadinanza
- `guest_type_code` - From @guest_type_id.code
- `guest_type_description` - From @guest_type_id.description
- `is_group_leader` - From @guest_type_id.is_leader (calculated)
- `tax_description` - From @tourist_tax_id.description
- `stay_check_in` - From @stay_id.check_in_date
- `stay_check_out` - From @stay_id.check_out_date
- `stay_nights` - From @stay_id.nights
- `facility_name` - From @stay_id.@facility_id.name

#### 7. `stay`
Accommodation stays (check-in to check-out period).
- `id` (PK)
- `facility_id` (FK to `facility`)
- `check_in_date` (D) - Check-in date (NOT NULL)
- `check_out_date` (D) - Check-out date (NOT NULL)
- `nights` - **Calculated field** (check_out_date - check_in_date)

**Validation**:
- Check-out date must be after check-in date (enforced in triggers)

**Calculated fields**:
- `nights`: Auto-calculated from date difference
- `stay_caption`: Display caption combining facility name and dates
  ```sql
  $facility_name || ' - ' || COALESCE(TO_CHAR($check_in_date, 'DD/MM/YYYY'), 'N/A')
  ```

**Alias columns**:
- `facility_name` - From @facility_id.name
- `facility_type` - From @facility_id.@facility_type_id.description
- `group_leader_name` - Calculated from guests with is_group_leader=TRUE

**Relations**:
- One stay has many guests (relation name: `@guests`)
- Each stay should have at least one group leader (guest_type code '17' or '18')

### Integration with Erpy Base

#### `erpyready.anagrafica`
Central registry for personal/company data. Used for:
- Facility owners/managers
- Guest personal information

**Key fields used**:
- `cognome` (surname)
- `nome` (name)
- `ragione_sociale` (full name/company name)
- `sesso` (gender): M/F → converted to 1/2 for police export
- `data_nascita` (birth date)
- `comune_nascita`, `provincia_nascita`, `stato_nascita` (birth place)
- `cittadinanza` (citizenship)

#### `glbl.comune`
Italian municipalities with ISTAT codes.
- Used for: birth municipality, document issue place
- Query: `WHERE $nome=:nome` → returns `code_istat`

#### `glbl.nazione`
Countries with codes for police reporting.
- Used for: birth country, citizenship
- Query: `WHERE $code=:code` → returns numeric code for police export

## Services

### PoliceExportService
Location: `packages/host/resources/services/police_export.py`

Generates police report in Italian ISTAT format (178 characters per guest).

**Methods**:
- `export_stay(stay_id)` - Returns string with 178-char lines (one per guest)
- `_format_guest_line(stay, guest)` - Formats single guest record
- `_pad(value, length, field_type)` - Pads values ('N'=numeric left-pad zeros, 'A'/'AN'=alpha right-pad spaces)
- `_get_comune_istat(comune_name)` - Fetches ISTAT code from glbl.comune
- `_get_country_code(country_code)` - Fetches numeric code from glbl.nazione

**Convenience function**:
```python
export_stay_to_file(db, stay_id, output_path=None)
```

#### Police Report Format (178 characters)

Fixed-width format with 15 fields:

| Field | Position | Length | Type | Description |
|-------|----------|--------|------|-------------|
| 1. Guest Type | 1-2 | 2 | N | 16=single, 17=family head, 18=group head, 19=family member, 20=group member |
| 2. Arrival Date | 3-12 | 10 | AN | Format: gg/mm/aaaa |
| 3. Days of Stay | 13-14 | 2 | N | Maximum 30 days |
| 4. Surname | 15-64 | 50 | A | Guest surname |
| 5. Name | 65-94 | 30 | A | Guest first name |
| 6. Gender | 95 | 1 | N | 1=Male, 2=Female |
| 7. Birth Date | 96-105 | 10 | AN | Format: gg/mm/aaaa |
| 8. Birth Municipality | 106-114 | 9 | N | ISTAT code |
| 9. Birth Province | 115-116 | 2 | A | Province code |
| 10. Birth Country | 117-125 | 9 | N | Country code |
| 11. Citizenship | 126-134 | 9 | N | Country code |
| 12. Document Type | 135-139 | 5 | AN | Document type code |
| 13. Document Number | 140-159 | 20 | AN | Document number |
| 14. Document Issue Place | 160-168 | 9 | N | Municipality ISTAT code |
| 15. Tourist Tax Code | 169-178 | 10 | N | Tax/exemption code (optional) |

**Padding rules**:
- N (Numeric): Left-pad with zeros, strip non-numeric chars
- A (Alpha): Right-pad with spaces
- AN (Alphanumeric): Right-pad with spaces

**Example guest line**:
```
17 01/06/2024 05 ROSSI                                             MARIO                         1 15/03/1980 058091    MI 100000100 100000100 IDENT AB123456           058091    0000000005
```

## UI Structure (Table Handlers)

### Menu Structure
Defined in `packages/host/menu.py`:

```
Host Management
├── Master Data
│   ├── Facilities
│   ├── Facility Types
│   ├── Guests
│   ├── Guest Types
│   ├── Document Types
│   └── Tourist Tax Rates
└── Operations
    └── Stays
```

### Key Table Handlers

#### `th_stay.py`
**View**:
- Shows: facility_name, check_in_date, check_out_date, nights, arrival_time, flight_number, group_leader_name
- Group leader name calculated via formulaColumn:
  ```python
  tbl.formulaColumn('group_leader_name', select=dict(
      table='host.guest',
      where='$stay_id=#THIS.id AND $is_group_leader IS TRUE',
      columns='$full_name'), name_long='Group Leader Name')
  ```
- Default order: `check_in_date DESC`

**Form**:
- Top section: facility_id, check_in_date, check_out_date, arrival_time, flight_number, safe_code
- Tab 1 (Guests): dialogTableHandler for @guests relation
- Tab 2 (Export Police Report): Button to export TXT file

**ViewFromFacility** (for display in facility form):
- Shows: check_in_date, check_out_date, nights, group_leader_name
- Order by: check_in_date DESC

**FormFromFacility** (for creating stays from facility):
- Top section: check_in_date, check_out_date, arrival_time, flight_number, safe_code
- Tab: Guests with multiButtonForm for inline guest creation

#### `th_guest.py`
**View**:
- Shows: facility_name, stay_check_in, stay_check_out, full_name, guest_type_description, tax_amount
- Default order: stay_check_in DESC, guest_type_code

**Form**:
- Top section: anagrafica_id, guest_type_id, tourist_tax_id, tax_amount (readonly)
- Document section: document_type_id, document_number, document_issued_by, document_issue_date, document_expiry_date

**FormFromStay** (for creating guests within a stay):
- Uses AnagraficaComponent from er_core for inline anagrafica creation
- Guest information: guest_type_id, tourist_tax_id, tax_amount
- Document information section

**ViewFromStay** (for display in stay form):
- Shows: full_name, guest_type_description, birth_date, tax_description, tax_amount
- Order by: guest_type_code, surname

### Resource Placement Best Practices

**CRITICAL RULE**: Custom view resources (like `ViewFromFacility`, `ViewFromStay`, etc.) must be defined in the resource file of the **table being displayed**, not in the resource file of the table that calls them.

**Example**:
```python
# In th_facility.py Form:
stays_tab.dialogTableHandler(relation='@stays',
                             viewResource='ViewFromFacility')

# The ViewFromFacility class MUST be in th_stay.py (NOT in th_facility.py)
# because it's displaying stay records
```

**Why**:
- Genropy's resource resolution looks for custom views in the target table's resource file
- This keeps view logic with the data it displays
- Prevents resource resolution errors and missing views
- Follows separation of concerns: each table's resource file defines how that table is viewed

**Pattern to follow**:
- `ViewFromX` classes go in the resource file of the **child table** (the many side of the relation)
- `FormFromX` classes go in the resource file of the **child table** (the many side of the relation)
- The parent table's form just references these resources by name

## Architectural Decisions

### 1. Anagrafica Integration
**Decision**: Store personal data in centralized `erpyready.anagrafica` registry.

**Rationale**:
- Avoid data duplication
- Guests can be linked to existing registry records
- Facility owners already in anagrafica
- Consistent with Erpy architecture

**Trade-off**: Requires erpyready package dependency

### 2. Guest Type System
**Decision**: Use official Italian guest type codes (16-20) with FK instead of boolean flag.

**Rationale**:
- Compliance with Italian regulations
- Supports full guest classification (not just leader/non-leader)
- Official codes required for police reporting
- More flexible for future requirements

**Evolution**: Originally designed with `is_group_leader` boolean, refactored to `guest_type_id` FK when official codes were provided.

### 3. Group Leader Model
**Decision**: Only group leaders (types 17, 18) require document tracking.

**Rationale**:
- Italian police reporting requirements
- Reduces data entry burden
- Family members/group members inherit leader's document reference

**Implementation**: Validation not enforced in database model, handled in application logic.

### 4. Guest-Stay Relationship
**Decision**: Each guest belongs to one stay (one-to-many), not many-to-many.

**Rationale**:
- Simplifies data model and reduces complexity
- If same person returns, create new guest record referencing same anagrafica
- Anagrafica contains permanent personal data, guest is stay-specific
- Easier queries and better performance
- Reflects reality: each guest record is for a specific booking

**Trade-off**:
- Multiple guest records for repeat visitors
- Mitigated by: easy to create new guest from existing anagrafica via UI

### 5. Calculated Fields
**Decision**: Use formula columns and triggers for automatic calculations.

**Rationale**:
- Automatic calculation ensures consistency
- No risk of stale data
- Genropy formula columns are performant
- Reduces application logic

**Examples**:
- `nights = check_out_date - check_in_date` (formula column)
- `is_leader = $code IN ('17', '18')` (formula column)
- `tax_amount` calculated via trigger based on nights × tax_rate for facility's municipality
- `group_leader_name` calculated via select formula from guests

### 6. Stay-centric View
**Decision**: UI shows stays with group leader name, not individual guests in list view.

**Rationale**:
- Natural mental model for accommodation management
- One stay = one booking
- Group leader is primary contact
- Detail view shows all guests

### 7. Italian Compliance
**Decision**: Follow official Italian codes and formats exactly.

**Rationale**:
- Legal compliance for police reporting
- Integration with Alloggiati Web webservice
- Future-proof for regulatory changes

**Implementation**:
- 5 official guest types (not customizable)
- 96 official document types (not customizable)
- 178-character police export format
- ISTAT codes for municipalities and countries

## Planned Features (GitHub Issues)

### Issue #1: Webservice Integration
**URL**: https://github.com/dgpaci/host/issues/1

**Goal**: Integrate with Alloggiati Web (Police SOAP webservice) and Ross1000.

**Components**:
1. **AlloggiatiWebClient** - SOAP client for police webservice
   - Methods: generate_token, test_schedine, send_schedine, download_ricevuta, download_tabelle
   - Based on MANUALEWS.pdf specifications

2. **AlloggiatiExporter** - 170-character record format (vs 178-char police export)
   - Field differences from police export to be analyzed

3. **Ross1000Exporter** - Format TBD
   - Integration specifications needed

4. **GuestReportingService** - Orchestrator service
   - Coordinates all exports and submissions
   - Error handling and retry logic

**Estimated effort**: 8-10 days

### Issue #2: Online Check-in System
**URL**: https://github.com/dgpaci/host/issues/2

**Goal**: Allow guests to complete their data online via signed links.

**Workflow**:
1. Staff creates stay with minimal info (name, email, phone)
2. System generates signed URL with 7-day expiration
3. Email sent to guest with check-in link
4. Guest completes 3-step wizard:
   - Step 1: Complete leader data (birth date, place, document)
   - Step 2: Add companions with their data
   - Step 3: Review and confirm
5. Stay status transitions: pending → ready → in_progress → completed
6. When "ready", trigger police/Ross1000 reporting

**New components**:
- `stay_status` lookup table (pending, ready, in_progress, completed, cancelled)
- `stay_token` table (token, stay_id, expiration, used)
- `/host/onlinecheckin` webpage (3-step wizard)
- Email templates
- TokenService for signed URL generation
- Auto-create anagrafica/guest records from online form

**Estimated effort**: ~10 days

## Data Sources

### CSV Files (provided by user)
- **tipo_alloggiato.csv** - 5 official guest types
- **documenti.csv** - 96 official document types
- **codici-tariffe-imposta-soggiorno.csv** - 9 tourist tax codes

### PDF Documentation
- **MANUALEWS.pdf** - Alloggiati Web SOAP webservice manual
  - 170-character record format (vs our 178-char police format)
  - SOAP methods: GenerateToken, Test, Send, etc.
  - Endpoint: https://alloggiatiweb.poliziadistato.it/service/service.asmx

## Development Notes

### Code Style
- All field names, code, and documentation in English
- Database schema names in lowercase with underscores
- Model files use Genropy conventions (Table class, config_db method)
- Table handler files use View/Form classes

### Testing Requirements
When implementing new features:
1. Test with real ISTAT codes from glbl.comune
2. Verify 178-character export format length
3. Test date validation (check-out > check-in)
4. Test tax calculation (nights × rate)
5. Test guest type constraints (at least one leader per stay)

### Known Limitations
1. Document fields not enforced as required for leaders in database (application logic only)
2. No automatic stay status management yet (planned in Issue #2)
3. No webservice integration yet (planned in Issue #1)
4. No email notification system yet (planned in Issue #2)

## Maintainer

- **Davide Paci** (@dgpaci)
- GitHub: https://github.com/dgpaci/host

## Version History

- **2.0.0** (2026-01-26): Major refactoring
  - Simplified data model: guest belongs to one stay (one-to-many instead of many-to-many)
  - Removed `stay_guest` junction table
  - Integration with `er_core:erpy_ready` instead of `erpy:erpy_base`
  - All lookup tables use `code` as primary key with `lookup=True`
  - Mandatory sysRecord for guest types (5 codes) and tourist tax codes (9 codes)
  - Improved tax calculation with municipality-specific rates via bag structure
  - Tax amount calculated via trigger instead of formula column

- **1.0.0** (2026-01-23): Initial release
  - Complete facility and guest management
  - Stay tracking with automatic calculations
  - Tourist tax management
  - Police report export (Italian format)
  - Package reorganization: moved to packages/host/ structure

## Quick Reference

### Common Queries

**Get all stays for a facility**:
```python
stays = db.table('host.stay').query(
    where='$facility_id=:fid',
    fid=facility_id,
    order_by='check_in_date DESC'
).fetch()
```

**Get group leader for a stay**:
```python
leader = db.table('host.guest').query(
    where='$stay_id=:sid AND @guest_type_id.code IN :codes',
    sid=stay_id,
    codes=['17', '18']
).fetchone()
```

**Calculate total tax for a stay**:
```python
total_tax = db.table('host.guest').query(
    columns='SUM($tax_amount) AS total',
    where='$stay_id=:sid',
    sid=stay_id
).fetchone()['total']
```

### Export Police Report

```python
from host.resources.services.police_export import export_stay_to_file

# Export to file
file_path = export_stay_to_file(db, stay_id, '/path/to/output.txt')

# Export to string
from host.resources.services.police_export import PoliceExportService
service = PoliceExportService(db)
content = service.export_stay(stay_id)
```

## Genropy Instance Setup

### Instance Structure

A Genropy instance requires the following structure:

```
instances/demohotel/
├── config/
│   └── instanceconfig.xml    # Instance configuration
├── root.py                     # WSGI entry point
├── site/                       # Site data (auto-created)
└── .gitignore
```

### Required Files

#### 1. `config/instanceconfig.xml`

```xml
<?xml version="1.0" ?>
<GenRoBag>
    <db dbname="demohotel"/>

    <packages>
        <gnrcore_sys pkgcode="gnrcore:sys"/>
        <gnrcore_adm pkgcode="gnrcore:adm"/>
        <gnr_it_glbl pkgcode="gnr_it:glbl"/>
        <erpyready pkgcode="erpyready:er_core"/>
        <host pkgcode="host:host"/>
    </packages>

    <authentication pkg="gnrcore:sys">
        <py_auth defaultTags="user" method="authenticate" pkg="adm"/>
    </authentication>

    <site>
        <wsgi mainpackage="host" debug="true" port="8090"/>
    </site>
</GenRoBag>
```

**Important notes**:
- Core packages use `gnrcore_` prefix and `pkgcode="gnrcore:sys"` format
- Italian global data: `gnr_it_glbl` with `pkgcode="gnr_it:glbl"`
- Erpy packages: `erpyready` with `pkgcode="erpyready:er_core"`
- Local packages: `host` with `pkgcode="host:host"`
- **erpyready is required** because host uses erpyreadydy.anagrafica` table

#### 2. `root.py`

Standard WSGI entry point:

```python
#!/usr/bin/env python
import sys
sys.stdout = sys.stderr
from gnr.web.gnrwsgisite import GnrWsgiSite
site = GnrWsgiSite(__file__)

def application(environ,start_response):
    return site(environ,start_response)

if __name__ == '__main__':
    from gnr.web.server import NewServer
    server=NewServer(__file__)
    server.run()
```

#### 3. `packages/host/webpages/index.py`

**Required** for mainpackage to work:

```python
#!/usr/bin/env pythonw
# -*- coding: utf-8 -*-

class GnrCustomWebPage(object):
    py_requires = 'frameindex'
    auth_workdate = 'admin,user'

    def windowTitle(self):
        owner_name = self.getPreference('instance_data.owner_name', pkg='adm')
        return owner_name or 'Host Management System'
```

**Without this file, the instance will not start properly.**

#### 4. `packages/host/menu.py`

Already exists in the package root. Defines menu structure:

```python
class Menu(object):
    def config(self, root, **kwargs):
        host = root.branch("Host Management", tags="host")

        # Master Data
        anagrafica = host.branch("Master Data", tags="masterdata")
        anagrafica.thpage("Facilities", table="host.facility")
        anagrafica.thpage("Facility Types", table="host.facility_type")
        anagrafica.thpage("Guests", table="host.guest")
        anagrafica.thpage("Guest Types", table="host.guest_type")
        anagrafica.thpage("Document Types", table="host.document_type")
        anagrafica.thpage("Tourist Tax Rates", table="host.tourist_tax")

        # Operations
        operations = host.branch("Operations", tags="operations")
        operations.thpage("Stays", table="host.stay")
```

### Database Migration

**Correct command**:
```bash
gnr db migrate demohotel
```

**NOT**: `gnrmigrate` (old command)

### Initialization Steps

1. Create PostgreSQL database:
   ```bash
   createdb -U postgres demohotel
   ```

2. Run migration:
   ```bash
   cd /Users/dgpaci/sviluppo/erpy_projects/host
   gnr db migrate demohotel
   ```

3. Load initial data:
   ```bash
   psql -U postgres -d demohotel -f initial_data.sql
   ```

4. Start instance:
   ```bash
   cd instances/demohotel
   python root.py
   # Or: gnrwsgi demohotel
   ```

5. Access at: http://localhost:8090

## Related Documentation

- README.md - User-facing documentation
- initial_data.sql - Lookup table data with official codes
- GitHub Issues - Planned features and enhancements
- instances/demohotel/README.md - Instance setup guide
