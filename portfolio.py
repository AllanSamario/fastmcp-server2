import json
from typing import Dict
from models import PortfolioFile


def load_portfolio(file_path: str) -> PortfolioFile:
    with open(file_path, "r") as f:
        return json.load(f)


def calculate_metal_summary(metal_data: dict) -> Dict:
    total_grams = 0.0
    total_invested = 0.0

    latest_price = metal_data["dailyPrices"][-1]["pricePerGram"]

    for tx in metal_data["transactions"]:
        if tx["type"] == "buy":
            if tx["unit"] == "grams":
                total_grams += tx["amount"]
                total_invested += tx["amount"] * latest_price
            elif tx["unit"] == "rupees":
                grams = tx["amount"] / latest_price
                total_grams += grams
                total_invested += tx["amount"]

    current_value = total_grams * latest_price
    profit = current_value - total_invested
    roi_percent = (profit / total_invested) * 100 if total_invested > 0 else 0

    return {
        "grams": round(total_grams, 4),
        "invested": round(total_invested, 2),
        "current_price": latest_price,
        "current_value": round(current_value, 2),
        "profit": round(profit, 2),
        "roi_percent": round(roi_percent, 2),
    }


def analyze_portfolio(file_path: str) -> Dict:
    data = load_portfolio(file_path)

    gold_summary = calculate_metal_summary(data["gold"])
    silver_summary = calculate_metal_summary(data["silver"])

    total_invested = gold_summary["invested"] + silver_summary["invested"]
    total_value = gold_summary["current_value"] + silver_summary["current_value"]
    total_profit = total_value - total_invested

    overall = {
        "invested": round(total_invested, 2),
        "value": round(total_value, 2),
        "profit": round(total_profit, 2),
        "roi_percent": round((total_profit / total_invested) * 100, 2)
        if total_invested > 0
        else 0,
    }

    return {
        "gold": gold_summary,
        "silver": silver_summary,
        "overall": overall,
    }