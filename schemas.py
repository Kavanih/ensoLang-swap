from pydantic import BaseModel


class Approve(BaseModel):
    chain_id: int
    account: str
    token_address: str
    amount: float

    class Config:
        json_schema_extra = {
            "example": {
                "chain_id": 1,
                "account": "0xd8da6bf26964af9d7eed9e03e53415d37aa96045",
                "token_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
                "amount": 100,
            }
        }
