BILLING = "PAY_PER_REQUEST"
TABLES = [
    {
        "TableName": "RequestLimits",
        "KeySchema": [
            {"AttributeName": "user_id", "KeyType": "HASH"},
        ],
        "AttributeDefinitions": [
            {"AttributeName": "user_id", "AttributeType": "S"},
        ],
        "BillingMode": BILLING,
        "_ttl": {
            "Enabled": True,
            "AttributeName": "ttl"
        },
    },
]
