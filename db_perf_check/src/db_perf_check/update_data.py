import uvloop

from sys import argv
from json import dumps

from db_perf_check.common import get_key_elements, get_config, generate_value
from db_perf_check.dynamo import (
    get_dynamo_resource,
    get_dynamo_table,
    simple_select as dynamo_select,
    data_creator as dynamo_update,
)
from db_perf_check.postgres import (
    get_connection,
    update as postgres_update,
    simple_select as postgres_select,
)
from db_perf_check.helpers import Timer

CONFIG = get_config()


async def main(db_type: str, silent: bool = False) -> None:
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

    k = f'{pref}{CONFIG["separator"]}{suff}'
    v = dumps(
        generate_value(
            CONFIG['prefix_name'],
            CONFIG['suffix_name'],
            CONFIG['number_of_prefixes'],
            CONFIG['number_of_suffixes'],
            sep=CONFIG['separator'],
        )
    )

    upd_elapsed = 0
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
                await dynamo_update(
                    table,
                    key=k,
                    data=v,
                )
            upd_elapsed = t.elapsed
            if not silent:
                print(f'Update result for "{k}" should be:', v)
                print(f'\nUpdate elapsed time: {t.elapsed:.4f} seconds\n')
            with Timer() as t:
                result = await dynamo_select(table, f'{pref}{CONFIG["separator"]}{suff}')
            if not silent:
                print('Result:', result)
                print(f'\nSelect elapsed time: {t.elapsed:.4f} seconds\n')
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
                await postgres_update(
                    conn,
                    table_name=CONFIG['postgres']['table_name'],
                    key=k,
                    value=v,
                )
            if not silent:
                print(f'Value for "{k}" should be:', v)
                print(f'\nUpdate elapsed time: {t.elapsed:.4f} seconds\n')
            upd_elapsed = t.elapsed
            with Timer() as t:
                result = await postgres_select(
                    conn,
                    table_name=CONFIG['postgres']['table_name'],
                    key=f'{pref}{CONFIG["separator"]}{suff}',
                )
            if not silent:
                print('Result:', result)
                print(f'\nSelect elapsed time: {t.elapsed:.4f} seconds\n')
        finally:
            await conn.close()
    else:
        print(f'Unknown db_type: {db_type}')
        exit(1)
    return upd_elapsed


if __name__ == '__main__':
    if len(argv) < 2:
        print('Usage: python create_data.py <db_type>')
        exit(1)
    db_type = argv[1]
    forever = False
    if len(argv) == 3 and argv[2] == 'forever':
        forever = True

    try:
        uvloop.install()
        import asyncio

        elapsed = []

        if forever:
            while True:
                if len(elapsed) > 500:
                    elapsed = [sum(elapsed) / len(elapsed)]
                elapsed.append(asyncio.run(main(db_type, True)))
        else:
            asyncio.run(main(db_type))

    except KeyboardInterrupt:
        print('Interrupted by user')
        if elapsed:
            print(f'\nMean elapsed time for updates: {sum(elapsed) / len(elapsed):.4f} seconds')
        exit(2)
