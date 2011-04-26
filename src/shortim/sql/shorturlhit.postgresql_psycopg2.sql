-- create index to improve trending topics performance
CREATE INDEX shortim_shorturlhit_date_idx ON shortim_shorturlhit (date);
