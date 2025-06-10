import random

import duckdb
from environs import Env
from faker import Faker
from loguru import logger
import pandas as pd
from time import sleep

env = Env()
env.read_env()

POSTGRES_HOST = env.str('POSTGRES_HOST')
POSTGRES_PORT = env.str('POSTGRES_PORT')
POSTGRES_DB = env.str('POSTGRES_DB')
POSTGRES_USER = env.str('POSTGRES_USER')
POSTGRES_PASSWORD = env.str('POSTGRES_PASSWORD')

MINIO_ENDPOINT = env.str("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = env.str("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = env.str("MINIO_SECRET_KEY")
MINIO_BUCKET = env.str("MINIO_BUCKET")
S3_PATH = f"s3://{MINIO_BUCKET}/datalake"

DATES = [f"2025-01-{n}" for n in range(1, 20)]
DOMAINS = [
    "google.com", "yahoo.com", "hotmail.com", "yandex.ru", "x.org", "y.org", "z.com", "a.com",
    "b.com", "gmail.com", "c.com", "d.com", "layer.cafe", "f.com"
]


def main():
    logger.info("generator started")
    con = duckdb.connect()

    con.execute(f"""

        SET extension_directory = '/root/.duckdb/extensions'

    """)

    # install extensions
    con.execute(f"""

        LOAD postgres;
        LOAD ducklake;
        LOAD httpfs;

    """)

    # create secrets
    con.execute(f"""

        CREATE SECRET (
            TYPE POSTGRES,
            HOST '{POSTGRES_HOST}',
            PORT {POSTGRES_PORT},
            DATABASE '{POSTGRES_DB}',
            USER '{POSTGRES_USER}',
            PASSWORD '{POSTGRES_PASSWORD}'
        );

        CREATE SECRET (
            TYPE S3,
            KEY_ID '{MINIO_ACCESS_KEY}',
            SECRET '{MINIO_SECRET_KEY}',
            ENDPOINT '{MINIO_ENDPOINT}',
            URL_STYLE 'path',
            USE_SSL false
        );

    """)

    # connect to datalake
    # including postgres and minio

    con.execute(f"""

        ATTACH '' as datalake_catalog (TYPE POSTGRES);

    """)

    con.execute(f"""
    
        ATTACH 'ducklake:postgres:dbname=datalake_catalog' AS warehouse
        (DATA_PATH '{S3_PATH}');
    
    """)

    con.execute(f"""
    
        CALL warehouse.set_option('parquet_row_group_size', '2_000_000' )
        
    """)

    fake = Faker()
    count = 0

    logger.info("adding records")
    while True:
        sleep(10)
        data = []
        for i in range(10000):
            domain = random.choice(DOMAINS)
            email = (fake.email(safe=True, domain=domain)).replace("@", f"{random.randint(1, 10000)}@")
            date = random.choice(DATES)
            name = fake.name()
            phone = fake.phone_number()
            data.append({
                "email": email,
                "date": date,
                "name": name,
                "phone": phone,
                "group_id": random.randint(1, 100),
            })
            if i % 1000 == 0:
                logger.info(f"created batch of {i} items so far")

        data_df = pd.DataFrame(data)

        try:
            query = (
                f"INSERT INTO warehouse.users "
                f"SELECT * FROM data_df"
            )
            con.execute(query)
            count += 1
            logger.info(f"added {count * len(data)} records")
        except Exception as ex:
            logger.error(f"failed to add {count} records: {str(ex)}")
            # logger.error(f"email {email} already exists")


if __name__ == '__main__':
    main()
