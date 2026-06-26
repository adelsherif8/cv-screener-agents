-- Seed skill graph with sample nodes
INSERT INTO skill_nodes (id, label, aliases, domains, embedding) VALUES
('typescript', 'TypeScript', '{"ts": ["TS", "tsconfig"]}', '{"domains": ["tech"]}', NULL),
('nursing', 'Nursing', '{"nurse": ["RN", "LPN"]}', '{"domains": ["healthcare"]}', NULL),
('accounting', 'Accounting', '{"accountant": ["CPA", "GAAP"]}', '{"domains": ["finance"]}', NULL);
