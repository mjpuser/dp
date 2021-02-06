INSERT INTO exchange (name) VALUES ('s3'), ('pipeline');

INSERT INTO func (name, config) VALUES ('vertex.s3.split', '{}');
INSERT INTO func (name, config) VALUES ('vertex.s3.register_dataset', '{"bucket": "raw"}');

INSERT INTO pipeline (name) VALUES ('raw data splitter'),
                                   ('dataset registrar');

INSERT INTO vertex (pipeline_id, name, exchange_in, routing_key_in, func, func_config)
VALUES ((SELECT id FROM pipeline WHERE name = 'raw data splitter'), 'split', 's3', '#', 'vertex.s3.split', '{}'),
       ((SELECT id FROM pipeline WHERE name = 'dataset registrar'), 'register', 's3', '#', 'vertex.s3.register_dataset', '{}');
