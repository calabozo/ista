CREATE DATABASE ista;

\connect ista

CREATE TABLE public.ista_measure
(
  id SERIAL PRIMARY KEY,
  serial text,
  date date,
  value NUMERIC(7,3)
);
COMMENT ON COLUMN ista_measure.serial is 'Serial number';
COMMENT ON COLUMN ista_measure.date is 'Date';
COMMENT ON COLUMN ista_measure.value  is 'Measure value';
CREATE INDEX dataidx on ista_measure(serial,date);
\copy public.ista_measure(serial,date,value) FROM '/docker-entrypoint-initdb.d/ista_measure.csv' DELIMITER ',' CSV HEADER;


CREATE TABLE public.ista_devices
(
  id SERIAL PRIMARY KEY,
  serial text,
  name text,
  type text
);
\copy public.ista_devices(serial,name,type) FROM '/docker-entrypoint-initdb.d/ista_devices.csv' DELIMITER ',' CSV HEADER;
