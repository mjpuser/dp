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

CREATE TABLE vertex (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES pipeline(id),
    name TEXT NOT NULL,
    exchange_in TEXT NOT NULL REFERENCES exchange(name),
    routing_key_in TEXT DEFAULT '#',
    func TEXT REFERENCES func(name),
    func_config JSON
);

CREATE TABLE knowledge_base (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE
);
