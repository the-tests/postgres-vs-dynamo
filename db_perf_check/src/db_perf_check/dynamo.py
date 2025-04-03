import aioboto3
from botocore.client import Config as BotoConfig
from boto3.dynamodb.conditions import Key


async def get_dynamo_resource(endpoint_url: str, region_name: str):
    session = aioboto3.Session()
    return await session.resource(
        'dynamodb',
        config=BotoConfig(
            connect_timeout=10,
            user_agent='perf_test',
            read_timeout=10,
            retries={'mode': 'standard'},
        ),
        endpoint_url=endpoint_url,
        region_name=region_name,
        aws_access_key_id='dummy',
        aws_secret_access_key='dummy',
    ).__aenter__()


async def get_dynamo_table(resource, table_name: str):
    try:
        await resource.create_table(**{
            "TableName": table_name,
            "AttributeDefinitions":[
                {'AttributeName': 'pk', 'AttributeType': 'S'},
            ],
            "KeySchema": [{'AttributeName': 'pk', 'KeyType': 'HASH'}],
            "ProvisionedThroughput": {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5},
            # "GlobalSecondaryIndexes": [{
            #     'IndexName': '2nd-index',
            #     'KeySchema': [
            #         {'AttributeName': 'pk', 'KeyType': 'HASH'},
            #     ],
            #     'Projection': {'ProjectionType': 'ALL'},
            #     'ProvisionedThroughput': {'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            # }]
        })
    except resource.meta.client.exceptions.ResourceInUseException:
        pass
    return await resource.Table(table_name)


async def data_creator(
        table,
        key: str,
        data: str,
    ) -> None:
    await table.put_item(
        Item={
            'pk': key,
            'data': data,
        },
        ReturnValues='NONE',
        ReturnConsumedCapacity='NONE',
        ReturnItemCollectionMetrics='SIZE',
        ReturnValuesOnConditionCheckFailure='NONE'
    )


async def simple_select(table: str, key: str) -> dict:
    result = await table.query(
                KeyConditionExpression=Key('pk').eq(key),
                ReturnConsumedCapacity='NONE',
            )
    return result['Items'][0]
