from typing import Dict, List, TypedDict


class DailyPrice(TypedDict):
    date: str
    pricePerGram: float


class Transaction(TypedDict):
    date: str
    type: str  # buy or sell
    amount: float
    unit: str  # grams or rupees


class MetalData(TypedDict):
    transactions: List[Transaction]
    dailyPrices: List[DailyPrice]


class PortfolioFile(TypedDict):
    gold: MetalData
    silver: MetalData