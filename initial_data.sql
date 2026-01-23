-- Initial data for Host Management System
-- Run this after package installation to populate lookup tables

-- Document Types
INSERT INTO host.document_type (code, description) VALUES
('CI', 'Carta d''Identità / Identity Card'),
('PASS', 'Passaporto / Passport'),
('PAT', 'Patente / Driver''s License'),
('PS', 'Permesso di Soggiorno / Residence Permit')
ON CONFLICT DO NOTHING;

-- Facility Types (examples)
INSERT INTO host.facility_type (code, description) VALUES
('HOTEL', 'Hotel'),
('BB', 'Bed & Breakfast'),
('APART', 'Apartment'),
('AGRITU', 'Agriturismo'),
('HOSTEL', 'Hostel'),
('VILLA', 'Villa'),
('CAMPING', 'Camping')
ON CONFLICT DO NOTHING;

-- Tourist Tax Rates (from Italian regulations - Corteno Golgi example)
-- Note: Adjust 'amount' field based on actual municipality rates
INSERT INTO host.tourist_tax (code, description, amount) VALUES
('0000000001', '5.1b) Esenzione per i minori fino al compimento del dodicesimo anno di età', 0.00),
('0000000002', '5.1a) Esenzione per gli iscritti all''anagrafe dei residenti del Comune', 0.00),
('0000000003', '5.1c) Esenzione per gli accompagnatori turistici di gruppi di almeno 25 partecipanti, gli autisti dei bus che li trasportano e gli insegnanti in gita scolastica', 0.00),
('0000000004', '5.1d) Esenzione per il personale dipendente del gestore della struttura ricettiva che ivi svolge attività lavorativa', 0.00),
('0000000005', '_NESSUNA ESENZIONE (TARIFFA PIENA)', 2.50),
('0000000006', '5.1e) Esenzione per persone non autosufficienti munite di certificazione medica e relativo accompagnatore', 0.00),
('0000000007', '5.1f) Esenzione per i volontari coordinati dalla Protezione Civile che alloggiano in strutture ricettive a seguito di provvedimenti adottati da autorità pubbliche, per fronteggiare eventi calamitosi', 0.00),
('0000000008', '5.1g) Esenzione per personale appartenente alla Polizia di Stato e locale, alle altre forze armate, nonché al corpo nazionale dei vigili del fuoco che, per esigenze di servizio, soggiornano nel Comune e limitatamente al servizio medesimo', 0.00),
('0000000009', '5.1h) Esenzione per i beneficiari di soggiorni gratuiti, per tali intendendosi quelli per i quali il gestore della struttura ricettiva non percepisce corrispettivo né dall''alloggiato né da altri', 0.00)
ON CONFLICT DO NOTHING;

-- Note: The amount for code '0000000005' (standard rate) is set to €2.50 as an example.
-- Adjust this value according to your municipality's actual tourist tax rate.
