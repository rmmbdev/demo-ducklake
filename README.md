# demo-ducklake
This is a demo project illustrating ducklake usage

## Run
1. build the project images
```bash
  docker-compose build
```

2. run
```bash
  docker compose up -d
```

## Doing analytics
After filling a couple of millions of data, you can test the setup.
1. enter duckdb or ui using `-ui` flag
```bash
   duckdb
```
2. setup the connection
```sql
LOAD postgres;
LOAD ducklake;
LOAD httpfs;

CREATE SECRET (
    TYPE POSTGRES,
    HOST 'localhost',
    PORT 5432,
    DATABASE 'datalake_catalog',
    USER 'postgres',
    PASSWORD 'postgres'
);

CREATE SECRET (
    TYPE S3,
    KEY_ID 'user01',
    SECRET 'secret_key',
    ENDPOINT 'localhost:9000',
    URL_STYLE 'path',
    USE_SSL false
);
     
ATTACH '' as datalake_catalog (TYPE POSTGRES);

ATTACH 'ducklake:postgres:dbname=datalake_catalog' AS warehouse
    (DATA_PATH 's3://users/datalake');
```

3. now it is possible to perform analytics
```sql
select * from warehouse.users where created_date='2025-01-12';

select * from warehouse.users where email like '%gmail%' and created_date='2025-01-12';

UPDATE warehouse.users set email=Replace(email,'gmail','google') where email like '%gmail%';

```