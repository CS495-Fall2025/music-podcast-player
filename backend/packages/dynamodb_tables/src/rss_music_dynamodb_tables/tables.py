BILLING = "PAY_PER_REQUEST"
TABLES = [
    {
        "TableName": "env:RSS_PLAYER_TOKEN_TABLE_NAME",
        "KeySchema": [
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "BillingMode": BILLING,
    },
]
