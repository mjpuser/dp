INSERT INTO exchange (name) VALUES ('s3'), ('pipeline');

INSERT INTO func (name, config) VALUES ('vertex.s3.split', '{}');
INSERT INTO func (name, config) VALUES ('vertex.s3.register_dataset', '["bucket"]');
INSERT INTO func (name, config) VALUES ('vertex.s3.write', '["bucket", "key"]');

INSERT INTO pipeline (name) VALUES ('raw data splitter'),
                                   ('dataset registrar'),
                                   ('census');

INSERT INTO vertex (pipeline_id, name, exchange_in, routing_key_in, func, func_config)
VALUES ((SELECT id FROM pipeline WHERE name = 'raw data splitter'), 'split', 's3', '#', 'vertex.s3.split', '{}'),
       ((SELECT id FROM pipeline WHERE name = 'dataset registrar'), 'register', 's3', '#', 'vertex.s3.register_dataset', '{"bucket": "raw"}'),
       ((SELECT id FROM pipeline WHERE name = 'census'), 'census_writer', 'pipeline', '#.census', 'vertex.s3.write', '{"bucket": "data", "key": "{message[id]}"}');
