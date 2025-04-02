import uvloop

from sys import argv
from typing import Iterator, Callable
from json import load, dumps

from db_perf_check.common import get_key_elements, get_config
from db_perf_check.dynamo import (
    get_dynamo_resource,
    get_dynamo_table,
    simple_select as dynamo_select
)
from db_perf_check.postgres import (
    get_connection,
    simple_select as postgres_select
)
from db_perf_check.helpers import Timer

CONFIG = get_config()


async def main(db_type: str) -> None:
    pref = get_key_elements(
        CONFIG['prefix_name'],
        True,
        num_of_elements=CONFIG['number_of_prefixes'],
    )
    suff = get_key_elements(
        CONFIG['suffix_name'],
        True,
        num_of_elements=CONFIG['number_of_suffixes'],
    )

    if db_type == 'dynamo':
        resource = await get_dynamo_resource(
            endpoint_url=CONFIG['dynamo']['endpoint_url'],
            region_name=CONFIG['dynamo']['region_name'],
        )
        try:
            table = await get_dynamo_table(
                resource,
                table_name=CONFIG['dynamo']['table_name'],
            )
            with Timer() as t:
                result = await dynamo_select(table, f'{pref}{CONFIG["separator"]}{suff}')
            print('RESULT:', result)
            print(f'\nElapsed time: {t.elapsed:.4f} seconds\n')
        finally:
            await resource.__aexit__(None, None, None)
    elif db_type == 'postgres':
        conn = await get_connection(
            user=CONFIG['postgres']['user'],
            password=CONFIG['postgres']['password'],
            database=CONFIG['postgres']['database'],
            host=CONFIG['postgres']['host'],
            port=CONFIG['postgres']['port'],
        )
        try:
            with Timer() as t:
                result = await postgres_select(
                    conn,
                    table_name=CONFIG['postgres']['table_name'],
                    key=f'{pref}{CONFIG["separator"]}{suff}',
                )
            print('RESULT:', result)
            print(f'\nElapsed time: {t.elapsed:.4f} seconds\n')
        finally:
            await conn.close()
    else:
        print(f'Unknown db_type: {db_type}')
        exit(1)



if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: python create_data.py <db_type>')
        exit(1)
    db_type = argv[1]

    try:
        uvloop.install()
        import asyncio
        asyncio.run(main(db_type))
    except KeyboardInterrupt:
        print('Interrupted by user')
        exit(2)
