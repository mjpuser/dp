INSERT INTO exchange (name) VALUES ('s3'), ('pipeline');

INSERT INTO func (name, config) VALUES ('vertex.s3.split', '{}');
INSERT INTO func (name, config) VALUES ('vertex.s3.register_dataset', '{}');
INSERT INTO func (name, config) VALUES ('vertex.s3.write', '["bucket", "key"]');
INSERT INTO func (name, config) VALUES ('vertex.vertex.filter', '["fields"]');

INSERT INTO pipeline (name) VALUES ('dataset'),
                                   ('census');

INSERT INTO vertex (pipeline_id, name, func, func_config)
VALUES ((SELECT id FROM pipeline WHERE name = 'dataset'), 'register', 'vertex.s3.register_dataset', '{}'),
       ((SELECT id FROM pipeline WHERE name = 'dataset'), 'split', 'vertex.s3.split', '{}'),
       ((SELECT id FROM pipeline WHERE name = 'dataset'), 'filter', 'vertex.vertex.filter', '{"fields": ["SERIALNO", "AGEP", "REGION", "WAGP", "SEX", "ST"]}'),
       ((SELECT id FROM pipeline WHERE name = 'dataset'), 'write', 'vertex.s3.write', '{"bucket": "data", "key": "{path}/{message[SERIALNO]}"}');

INSERT INTO vertex_connection (sender, receiver)
VALUES
    (
     (SELECT id FROM vertex WHERE pipeline_id = (SELECT id FROM pipeline WHERE name = 'dataset') AND name = 'register'),
     (SELECT id FROM vertex WHERE pipeline_id = (SELECT id FROM pipeline WHERE name = 'dataset') AND name = 'split')
    ),
    (
     (SELECT id FROM vertex WHERE pipeline_id = (SELECT id FROM pipeline WHERE name = 'dataset') AND name = 'split'),
     (SELECT id FROM vertex WHERE pipeline_id = (SELECT id FROM pipeline WHERE name = 'dataset') AND name = 'filter')
    ),
    (
     (SELECT id FROM vertex WHERE pipeline_id = (SELECT id FROM pipeline WHERE name = 'dataset') AND name = 'filter'),
     (SELECT id FROM vertex WHERE pipeline_id = (SELECT id FROM pipeline WHERE name = 'dataset') AND name = 'write')
    );
