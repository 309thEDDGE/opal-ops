#!/bin/bash
/usr/bin/mc alias set localminio http://minio:9000 minioadmin minioadmin
/usr/bin/mc mb localminio/kinds
/usr/bin/mc mb localminio/scripts
/usr/bin/mc mb localminio/data
