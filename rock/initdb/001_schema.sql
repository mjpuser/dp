CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE func (
    name TEXT PRIMARY KEY NOT NULL,
    config JSON
);

CREATE TABLE exchange (
    name TEXT PRIMARY KEY NOT NULL
);

CREATE TABLE pipeline (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    name TEXT NOT NULL
);

CREATE TABLE dataset (
    name TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE vertex (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES pipeline(id),
    name TEXT NOT NULL,
    func TEXT REFERENCES func(name),
    func_config JSON
);

CREATE TABLE vertex_connection (
    receiver UUID REFERENCES vertex(id),
    sender UUID REFERENCES vertex(id)
);

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE
);
