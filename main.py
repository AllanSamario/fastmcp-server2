import sys
from pathlib import Path
from fastmcp import FastMCP
import json
# from mcp.server.fastmcp import FastMCP
from portfolio import analyze_portfolio
from ai_engine import generate_ai_analysis

mcp = FastMCP("Precious Metals Portfolio AI")


@mcp.tool()
def analyze_precious_metals() -> str:
    data_path = Path(__file__).parent / "data" / "portfolio_export.json"

    with open(data_path, "r") as f:
        portfolio = json.load(f)

    transactions = portfolio["transactions"]
    daily_prices = portfolio["dailyPrices"]

    # Get latest daily price
    latest_price = max(daily_prices, key=lambda x: x["date"])

    gold_price_now = latest_price["goldInrPerGram"]
    silver_price_now = latest_price["silverInrPerGram"]

    gold_grams = 0
    silver_grams = 0

    for t in transactions:
        amount = t["amount"]
        unit = t["unit"]
        metal = t["metal"]
        price_per_gram = t["pricePerGram"]

        # Convert rupees to grams if needed
        if unit == "rupees":
            grams = amount / price_per_gram
        else:
            grams = amount

        if metal == "gold":
            gold_grams += grams
        elif metal == "silver":
            silver_grams += grams

    gold_value = gold_grams * gold_price_now
    silver_value = silver_grams * silver_price_now
    total_value = gold_value + silver_value

    gold_alloc = (gold_value / total_value) * 100 if total_value else 0
    silver_alloc = (silver_value / total_value) * 100 if total_value else 0

    return f"""
📊 Precious Metals Portfolio Analysis

Total Portfolio Value: ₹{total_value:,.2f}

Gold:
- Total Grams: {gold_grams:.2f}
- Current Price: ₹{gold_price_now:,.2f} per gram
- Current Value: ₹{gold_value:,.2f}
- Allocation: {gold_alloc:.1f}%

Silver:
- Total Grams: {silver_grams:.2f}
- Current Price: ₹{silver_price_now:,.2f} per gram
- Current Value: ₹{silver_value:,.2f}
- Allocation: {silver_alloc:.1f}%
"""

    data_path = Path(__file__).parent / "data" / "portfolio_export.json"

    with open(data_path, "r") as f:
        portfolio = json.load(f)

    gold_oz = portfolio["gold"]["ounces"]
    gold_price = portfolio["gold"]["price"]
    silver_oz = portfolio["silver"]["ounces"]
    silver_price = portfolio["silver"]["price"]

    gold_value = gold_oz * gold_price
    silver_value = silver_oz * silver_price
    total = gold_value + silver_value

    return f"""
Portfolio Analysis

Total Value: ${total:,.2f}

Gold: {gold_oz} oz at ${gold_price} = ${gold_value:,.2f}
Silver: {silver_oz} oz at ${silver_price} = ${silver_value:,.2f}

Gold Allocation: {(gold_value/total)*100:.1f}%
Silver Allocation: {(silver_value/total)*100:.1f}%
"""

if __name__ == "__main__":
    print("MCP Server Started", file=sys.stderr)
    mcp.run()