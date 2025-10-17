from decimal import Decimal

from pydantic import ValidationError
from pytest import mark

from nobitex.schema.orderbook import OrderBook, OrderBookEntry, all_order_books_T


class TestOrderBookEntry:
    @mark.parametrize(
        "input_data, expected_price, expected_quantity",
        [
            (["50000.0", "0.1"], Decimal("50000.0"), Decimal("0.1")),  # test with strings
            ([50000, 0.1], Decimal("50000"), Decimal("0.1")),  # test with int
            ([70000.0, 0.3], Decimal("70000.0"), Decimal("0.3")),  # test with floats
            (["60000.0", "0.2"], Decimal("60000.0"), Decimal("0.2")),  # test with list
            (("60000.0", "0.2"), Decimal("60000.0"), Decimal("0.2")),  # test with tuple
            ({"price": "60000.0", "quantity": "0.2"}, Decimal("60000.0"), Decimal("0.2")),  # test with dict
        ],
    )
    def test_order_book_entry_variants(self, input_data, expected_price, expected_quantity):
        """Test various input formats for OrderBookEntry."""
        entry = OrderBookEntry.model_validate(input_data)
        assert entry.price == expected_price
        assert entry.quantity == expected_quantity

    @mark.parametrize(
        "json_data, expected_price, expected_quantity",
        [
            ('["50000.0", "0.1"]', Decimal("50000.0"), Decimal("0.1")),
            ('["60000.0", "0.2"]', Decimal("60000.0"), Decimal("0.2")),
            ('{"price": "70000.0", "quantity": "0.3"}', Decimal("70000.0"), Decimal("0.3")),
        ],
    )
    def test_order_book_entry_variants_json(self, json_data, expected_price, expected_quantity):
        """Test various JSON input formats for OrderBookEntry."""
        entry = OrderBookEntry.model_validate_json(json_data)
        assert entry.price == expected_price
        assert entry.quantity == expected_quantity

    @mark.parametrize(
        "invalid_input",
        [
            ["50000.0"],  # Missing quantity
            ["50000.0", "0.1", "extra"],  # Extra element
            12345,  # Not a list or dict
            {"price": "50000.0"},  # Missing quantity in dict
        ],
    )
    def test_order_book_entry_invalid_variants(self, invalid_input):
        """Test invalid input formats for OrderBookEntry."""
        try:
            OrderBookEntry.model_validate(invalid_input)
        except ValidationError as e:
            assert "1 validation error" in str(e)

    @mark.parametrize(
        "input_data,json_data",
        [
            (["80000.0", "0.4"], '{"price":"80000.0","quantity":"0.4"}'),
            (["90000.0", "0.5"], '{"price":"90000.0","quantity":"0.5"}'),
            ({"price": "100000.0", "quantity": "0.6"}, '{"price":"100000.0","quantity":"0.6"}'),
        ],
    )
    def test_order_book_entry_json(self, input_data, json_data):
        """Test various input formats for OrderBookEntry JSON serialization."""
        entry = OrderBookEntry.model_validate(input_data)
        assert entry.model_dump_json() == json_data

    @mark.parametrize(
        "input_data,expected_dump",
        [
            (["80000.0", "0.4"], {"price": Decimal("80000.0"), "quantity": Decimal("0.4")}),
            (["90000.0", "0.5"], {"price": Decimal("90000.0"), "quantity": Decimal("0.5")}),
            ({"price": "100000.0", "quantity": "0.6"}, {"price": Decimal("100000.0"), "quantity": Decimal("0.6")}),
        ],
    )
    def test_order_book_entry_dump(self, input_data, expected_dump):
        """Test various input formats for OrderBookEntry dict serialization."""
        entry = OrderBookEntry.model_validate(input_data)
        assert entry.model_dump() == expected_dump


class TestOrderBook:
    @mark.parametrize(
        "sample_orderbook",
        [
            {
                "asks": [["1476091000", "1.016"], ["1479700000", "0.2561"]],
                "bids": [["1470001120", "0.126571"], ["1470000000", "0.818994"]],
            },
            # -------------------------------------------------------------
            {"asks": [], "bids": []},
            # -------------------------------------------------------------
            {
                "status": "ok",
                "lastUpdate": 1644991756704,
                "lastTradePrice": "35650565900",
                "asks": [["1476091000", "1.016"], ["1479700000", "0.2561"]],
                "bids": [["1470001120", "0.126571"], ["1470000000", "0.818994"]],
            },
            # -------------------------------------------------------------
            {"status": "ok", "lastUpdate": 1644991756704, "lastTradePrice": "35650565900", "asks": [], "bids": []},
        ],
    )
    def test_order_book(self, sample_orderbook):
        """Test OrderBook with various sample data."""
        order_book = OrderBook.model_validate(sample_orderbook)

        assert len(order_book.bids) == len(sample_orderbook["bids"])
        assert len(order_book.asks) == len(sample_orderbook["asks"])
        for i, bid in enumerate(order_book.bids):
            assert bid.price == Decimal(sample_orderbook["bids"][i][0])
            assert bid.quantity == Decimal(sample_orderbook["bids"][i][1])
        for i, ask in enumerate(order_book.asks):
            assert ask.price == Decimal(sample_orderbook["asks"][i][0])
            assert ask.quantity == Decimal(sample_orderbook["asks"][i][1])
        assert isinstance(order_book, OrderBook)

    @mark.parametrize(
        "sample_orderbook_json",
        [
            """
        {"asks": [
            ["1476091000", "1.016"],
            ["1479700000", "0.2561"]
        ],
        "bids": [
            ["1470001120", "0.126571"],
            ["1470000000", "0.818994"]
        ]},
        """,
            # -------------------------------------------------------------
            """
        {"asks": [],
        "bids": []}
        """,
        ],
    )
    def test_order_book_json(self, sample_orderbook_json):
        """Test OrderBook with various sample JSON data."""
        order_book = OrderBook.model_validate_json(sample_orderbook_json)
        import json

        data = json.loads(sample_orderbook_json)

        assert len(order_book.bids) == len(data["bids"])
        assert len(order_book.asks) == len(data["asks"])
        for i, bid in enumerate(order_book.bids):
            assert bid.price == Decimal(data["bids"][i][0])
            assert bid.quantity == Decimal(data["bids"][i][1])
        for i, ask in enumerate(order_book.asks):
            assert ask.price == Decimal(data["asks"][i][0])
            assert ask.quantity == Decimal(data["asks"][i][1])
        assert isinstance(order_book, OrderBook)


@mark.parametrize(
    "all_order_books_data",
    [
        """
{
  "BTCIRT": {
    "lastUpdate": 1644991756704,
    "asks": [
      ["1476091000", "1.016"],
      ["1479700000", "0.2561"]
    ],
    "bids": [
      ["1470001120", "0.126571"],
      ["1470000000", "0.818994"]
    ]
  },
  "USDTIRT": {
    "lastUpdate": 1644991767392,
    "asks": [
      ["277990", "6688.3"],
      ["278000", "28185.03"]
    ],
    "bids": [
      ["277960", "119.31"],
      ["271240", "1079.75"]
    ]
  },
  "USDTBTC": {
    "lastUpdate": 1644991767392,
    "asks": [],
    "bids": []
  }
}
"""
    ],
)
def test_all_order_books_T(all_order_books_data):
    """Test AllOrderBooks with sample data."""
    all_order_books = all_order_books_T.validate_json(all_order_books_data)

    assert "BTCIRT" in all_order_books
    assert "USDTIRT" in all_order_books

    btcirt_order_book = all_order_books["BTCIRT"]
    usdtirt_order_book = all_order_books["USDTIRT"]

    assert isinstance(btcirt_order_book, OrderBook)
    assert isinstance(usdtirt_order_book, OrderBook)

    assert btcirt_order_book.bids[0].price == Decimal("1470001120")
    assert usdtirt_order_book.asks[1].quantity == Decimal("28185.03")
