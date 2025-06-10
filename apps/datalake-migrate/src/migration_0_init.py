import duckdb
from environs import Env
from loguru import logger

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


def main():
    logger.info("Started!")
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

    # create table
    con.execute(f"""
        
        CREATE TABLE IF NOT EXISTS warehouse.users (
            email        text,
            created_date date,
            name         text,
            phone        text,
            group_id     text
        );
        ALTER TABLE warehouse.users set PARTITIONED BY (created_date);
        
    
    """)

    logger.info("Done!")


if __name__ == '__main__':
    main()
