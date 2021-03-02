#!/usr/bin/env sh

echo "Configuring minio instance"
mc config host add s3 http://s3:9000 minio minio678
mc admin config set s3/ notify_amqp:1 enable="on" exchange="s3" exchange_type="topic" no_wait="false"  url="amqp://admin:admin@rabbitmq:5672" auto_deleted="false" delivery_mode="0" durable="false" internal="false" routing_key=""
mc admin service restart s3/

for bucket in raw meta data
do
  echo "Add $bucket bucket"
  mc mb -p s3/$bucket
done


mc event add -p s3/raw arn:minio:sqs::1:amqp

echo "Done configuring minio instance"

