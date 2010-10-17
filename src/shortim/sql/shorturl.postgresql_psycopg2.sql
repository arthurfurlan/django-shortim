-- change the serial column to use "bigint" instead of "int"
ALTER TABLE shortim_shorturl ALTER COLUMN id TYPE bigint;
CREATE UNIQUE INDEX shortim_shorturl_url_idx ON shortim_shorturl (url);
