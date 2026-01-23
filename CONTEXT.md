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
        └── webpages/         # Web pages (empty for now)
```

## Database Architecture

### Schema: `host`

All tables use the `host` SQL schema. Integration with `erpy_base` schema for anagrafica (registry) and `glbl` schema for ISTAT codes.

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
- `anagrafica_id` (FK to `erpy_base.anagrafica`) - Owner/Manager
- `name` - Facility name
- `facility_type_id` (FK to `facility_type`)

**Relations**:
- Many facilities per anagrafica (owner can have multiple facilities)
- One facility_type per facility

#### 6. `guest`
Guest registry with document information.
- `id` (PK)
- `anagrafica_id` (FK to `erpy_base.anagrafica`) - Personal data
- `document_type_id` (FK to `document_type`)
- `document_number` - Document number
- `document_issued_by` - Issuing authority/place
- `document_issue_date` - Issue date (D)
- `document_expiry_date` - Expiry date (D)

**Business rules**:
- Document fields are **required only for group leaders** (guest types 17, 18)
- Personal data (name, surname, birth date, etc.) stored in `erpy_base.anagrafica`
- One guest can have multiple stays

**Alias columns** (for UI display):
- `guest_name` - From anagrafica.ragione_sociale
- `guest_birth_date` - From anagrafica.data_nascita
- `guest_citizenship` - From anagrafica.cittadinanza

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

#### 8. `stay_guest` (Many-to-Many Junction Table)
Links stays to guests with tax information.
- `id` (PK)
- `stay_id` (FK to `stay`)
- `guest_id` (FK to `guest`)
- `guest_type_id` (FK to `guest_type`) - **Required**
- `tourist_tax_id` (FK to `tourist_tax`)
- `tax_amount` - **Calculated field** (nights × tax_rate)

**Business logic**:
- Each stay must have at least one group leader (guest_type code '17' or '18')
- Tax amount auto-calculated: `@stay_id.nights * @tourist_tax_id.amount`
- Multiple guests per stay, each with their own tax rate

**Alias columns for UI**:
- `guest_name` - From @guest_id.@anagrafica_id.ragione_sociale
- `guest_surname` - From @guest_id.@anagrafica_id.cognome
- `guest_birth_date` - From @guest_id.@anagrafica_id.data_nascita
- `guest_type_code` - From @guest_type_id.code
- `guest_type_description` - From @guest_type_id.description
- `is_group_leader` - From @guest_type_id.is_leader (calculated)
- `tax_description` - From @tourist_tax_id.description

**Formula column**:
```python
tbl.formulaColumn('tax_amount',
                 '@stay_id.nights * @tourist_tax_id.amount',
                 dtype='N', name_long='Tax Amount')
```

### Integration with Erpy Base

#### `erpy_base.anagrafica`
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
- `_format_guest_line(stay, stay_guest)` - Formats single guest record
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
- Shows: facility_name, check_in_date, check_out_date, nights, group_leader_name
- Group leader name calculated via SQL:
  ```sql
  SELECT g.ragione_sociale
  FROM host.stay_guest sg
  JOIN host.guest gu ON sg.guest_id = gu.id
  JOIN erpy_base.anagrafica g ON gu.anagrafica_id = g.id
  JOIN host.guest_type gt ON sg.guest_type_id = gt.id
  WHERE sg.stay_id = $id AND gt.code IN ('17', '18')
  LIMIT 1
  ```
- Default order: `check_in_date DESC`

**Form**:
- Top section: facility_id, check_in_date, check_out_date, nights (readonly)
- Tab 1 (Guests): dialogTableHandler for stay_guests relation
- Tab 2 (Export Police Report): Button to export TXT file

**ViewFromStay** (stay_guests relation):
- Shows: guest_name, guest_type_description, guest_birth_date, tax_description, tax_amount
- Order by: guest_type_code, guest_surname

**FormFromStay** (stay_guests relation):
- Fields: guest_id (with birth_date, citizenship auxColumns), guest_type_id, tourist_tax_id, tax_amount (readonly)

#### `th_guest.py`
**View**:
- Shows: guest_name, guest_birth_date, guest_citizenship, document_type_description, document_number

**Form**:
- Top section: anagrafica_id (with birth_date, citizenship auxColumns)
- Tab 1 (Document): document_type_id, document_number, document_issued_by, document_issue_date, document_expiry_date
- Tab 2 (Stays): dialogTableHandler for stays relation

## Architectural Decisions

### 1. Anagrafica Integration
**Decision**: Store personal data in centralized `erpy_base.anagrafica` registry.

**Rationale**:
- Avoid data duplication
- Guests can be linked to existing registry records
- Facility owners already in anagrafica
- Consistent with Erpy architecture

**Trade-off**: Requires erpy_base package dependency

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

### 4. Calculated Fields
**Decision**: Use formula columns for nights, tax_amount, is_leader.

**Rationale**:
- Automatic calculation ensures consistency
- No risk of stale data
- Genropy formula columns are performant
- Reduces application logic

**Examples**:
- `nights = check_out_date - check_in_date`
- `tax_amount = @stay_id.nights * @tourist_tax_id.amount`
- `is_leader = $code IN ('17', '18')`

### 5. Stay-centric View
**Decision**: UI shows stays with group leader name, not individual guests in list view.

**Rationale**:
- Natural mental model for accommodation management
- One stay = one booking
- Group leader is primary contact
- Detail view shows all guests

### 6. Italian Compliance
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
leader = db.table('host.stay_guest').query(
    where='$stay_id=:sid AND @guest_type_id.code IN :codes',
    sid=stay_id,
    codes=['17', '18']
).fetchone()
```

**Calculate total tax for a stay**:
```python
total_tax = db.table('host.stay_guest').query(
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

## Related Documentation

- README.md - User-facing documentation
- initial_data.sql - Lookup table data with official codes
- GitHub Issues - Planned features and enhancements
