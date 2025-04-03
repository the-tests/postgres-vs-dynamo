import asyncpg


async def get_connection(user, password, database, host, port):
    conn = await asyncpg.connect(
        user=user,
        password=password,
        database=database,
        host=host,
        port=port,
    )
    return conn


async def create_table(conn, table_name):
    try:
        await conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                pk VARCHAR(255) PRIMARY KEY,
                data JSONB
            );
        """)
    except asyncpg.exceptions.DuplicateTableError:
        print(f'Table {table_name} already exists.')


async def data_creator(conn, table_name: str, key: str, data: str) -> None:
    await conn.execute(
        f"""INSERT INTO {table_name} (pk, data) VALUES ($1, $2)
        ON CONFLICT (pk)
        DO UPDATE SET data = $2;
        """,
        key,
        data,
    )


async def simple_select(conn, table_name: str, key: str) -> dict:
    result = await conn.fetchrow(
        f'SELECT pk, data FROM {table_name} WHERE pk = $1',
        key,
    )
    return result


async def update(conn, table_name: str, key: str, value: str) -> dict:
    await conn.execute(
        f'UPDATE {table_name} SET data = $2 WHERE pk = $1',
        key,
        value,
    )
