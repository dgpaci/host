-- Migration script to rename _id fields to _code
-- Run this on your database

BEGIN;

-- Rename guest table fields
ALTER TABLE host.host_guest RENAME COLUMN guest_type_id TO guest_type_code;
ALTER TABLE host.host_guest RENAME COLUMN tourist_tax_id TO tourist_tax_code;
ALTER TABLE host.host_guest RENAME COLUMN document_type_id TO document_type_code;

-- Rename facility table field
ALTER TABLE host.host_facility RENAME COLUMN facility_type_id TO facility_type_code;

COMMIT;
