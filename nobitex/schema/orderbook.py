from decimal import Decimal
from typing import Any, List

from pydantic import BaseModel, Field, TypeAdapter, model_validator


class OrderBookEntry(BaseModel):
    price: Decimal = Field(..., description="The price of the order")
    quantity: Decimal = Field(..., description="The quantity of the order")

    @model_validator(mode="before")
    @classmethod
    def parse_list(cls, data: Any):
        if isinstance(data, (list, tuple)) and len(data) == 2:
            return {"price": data[0], "quantity": data[1]}
        return data


class OrderBook(BaseModel):
    bids: List[OrderBookEntry] = Field(..., description="List of bid orders")
    asks: List[OrderBookEntry] = Field(..., description="List of ask orders")


all_order_books_T = TypeAdapter(dict[str, OrderBook])
