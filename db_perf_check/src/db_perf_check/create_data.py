import uvloop

from sys import argv
from typing import Iterator, Callable
from json import load, dumps

from db_perf_check.common import (
    get_key_elements,
    generate_value,
)
from db_perf_check.dynamo import (
    get_dynamo_resource,
    get_dynamo_table,
    data_creator as dynamo_creator
)
from db_perf_check.postgres import (
    get_connection,
    create_table,
    data_creator as postgres_creator
)
from db_perf_check.helpers import Timer


def get_config():
    with open('config.json', 'r') as f:
        return load(f)


CONFIG = get_config()


def iter_through_keys() -> Iterator[str]:
    for el in get_key_elements(
        CONFIG['prefix_name'],
        False,
        num_of_elements=CONFIG['number_of_prefixes'],
    ):
        for el2 in get_key_elements(
            CONFIG['suffix_name'],
            False,
            num_of_elements=CONFIG['number_of_suffixes'],
        ):
            yield {f'{el}{CONFIG['separator']}{el2}': generate_value(
                CONFIG['prefix_name'],
                CONFIG['suffix_name'],
                CONFIG['number_of_prefixes'],
                CONFIG['number_of_suffixes'],
                sep=CONFIG['separator'],
            )}


async def create_data(connection, create_func: Callable, table_name: str = None) -> None:
    try:
        with Timer() as t:
            for item in iter_through_keys():
                key = list(item.keys())[0]
                data = dumps(list(item.values())[0])
                if table_name is not None:
                    await create_func(connection, table_name, key, data)
                else:
                    await create_func(connection, key, data)
    finally:
        print(f'\nElapsed time: {t.elapsed:.4f} seconds\n')


async def main(db_type):
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
            await create_data(table, dynamo_creator)
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
            await create_table(
                conn,
                table_name=CONFIG['postgres']['table_name'],
            )
            await create_data(
                conn,
                postgres_creator,
                CONFIG['postgres']['table_name'],
            )
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
