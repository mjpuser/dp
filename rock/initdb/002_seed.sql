INSERT INTO exchange (name) VALUES ('s3'), ('pipeline');

INSERT INTO func (name, config) VALUES ('vertex.s3.split', '{}');

INSERT INTO pipeline (name) VALUES ('s3 splitter');

INSERT INTO vertex (pipeline_id, name, exchange_in, routing_key_in, func, func_config)
VALUES ((SELECT id FROM pipeline WHERE name = 's3 splitter'), 'split', 's3', '#', 'vertex.s3.split', '{}');
