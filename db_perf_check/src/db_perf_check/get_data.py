import uvloop

from json import loads
from sys import argv

from db_perf_check.common import get_key_elements, get_config
from db_perf_check.dynamo import (
    get_dynamo_resource,
    get_dynamo_table,
    simple_select as dynamo_select,
    # select_multiple as dynamo_select_multiple,
)
from db_perf_check.postgres import (
    get_connection,
    simple_select as postgres_select,
    select_multiple as postgres_select_multiple,
)
from db_perf_check.helpers import Timer

CONFIG = get_config()


async def main(db_type: str, silent: bool = False) -> None:
    elapsed_simple = 0
    elapsed_multiple = 0
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
        resource = await get_dynamo_resource(**CONFIG['dynamo']['connection_info'])
        try:
            table = await get_dynamo_table(
                resource,
                table_name=CONFIG['dynamo']['table_name'],
            )
            with Timer() as t:
                result = await dynamo_select(table, f'{pref}{CONFIG["separator"]}{suff}')
            elapsed_simple = t.elapsed
            related_elements = loads(result['data'])['related_elements']
            if not silent:
                print('RESULT (single):', result)
                print(f'\nElapsed time: {t.elapsed:.4f} seconds\n')
            # TODO: it is not possible to get multiple keys in one query
            # with Timer() as t:
            #     result = await dynamo_select_multiple(
            #         table,
            #         keys=related_elements,
            #     )
            # elapsed_multiple = t.elapsed
            # if not silent:
            #     print('RESULT:', result)
            #     print(f'\nElapsed multiple time: {t.elapsed:.4f} seconds\n')
        finally:
            await resource.__aexit__(None, None, None)
    elif db_type == 'postgres':
        conn = await get_connection(**CONFIG['postgres']['connection_info'])
        try:
            with Timer() as t:
                result = await postgres_select(
                    conn,
                    table_name=CONFIG['postgres']['table_name'],
                    key=f'{pref}{CONFIG["separator"]}{suff}',
                )
            related_elements = loads(result['data'])['related_elements']
            elapsed_simple = t.elapsed
            if not silent:
                print('RESULT (single):', result)
                print(f'\nElapsed time: {t.elapsed:.4f} seconds\n')
            with Timer() as t:
                result = await postgres_select_multiple(
                    conn,
                    table_name=CONFIG['postgres']['table_name'],
                    keys=related_elements,
                )
            elapsed_multiple = t.elapsed
            if not silent:
                print('RESULT (multiple):', '\n'.join([str(x) for x in result]))
                print(f'\nElapsed time: {t.elapsed:.4f} seconds\n')
        finally:
            await conn.close()
    else:
        print(f'Unknown db_type: {db_type}')
        exit(1)
    return elapsed_simple, elapsed_multiple


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
                    elapsed = [
                        (
                            sum([x[0] for x in elapsed]) / len(elapsed),
                            sum([x[1] for x in elapsed]) / len(elapsed)
                        )
                    ]
                elapsed.append(asyncio.run(main(db_type, True)))
        else:
            asyncio.run(main(db_type))
    except KeyboardInterrupt:
        print('Interrupted by user')
        if elapsed:
            print(
                f'\nMean elapsed time for simple selects: {sum([x[0] for x in elapsed]) / len(elapsed):.4f}'
                ' seconds'
            )
            print(
                f'Mean elapsed time for complex selects: {sum([x[1] for x in elapsed]) / len(elapsed):.4f}'
                ' seconds'
            )
        exit(2)
