CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE dataset (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    path TEXT NOT NULL
);

CREATE TABLE pipeline (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    dataset_id UUID REFERENCES dataset(id),
    name TEXT NOT NULL
);

CREATE TABLE vertex (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    pipeline_id UUID REFERENCES pipeline(id),
    name TEXT NOT NULL,
    routing_key_in TEXT,
    routing_key_out TEXT
);

CREATE TABLE "knowledge-base" (
    id UUID PRIMARY KEY NOT NULL DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE
);
