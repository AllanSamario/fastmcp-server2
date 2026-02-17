import sys
import os
import json
from pathlib import Path
from fastmcp import FastMCP
from google import generativeai as genai

mcp = FastMCP("Precious Metals Portfolio AI")

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


@mcp.tool()
def analyze_precious_metals() -> str:
    data_path = Path(__file__).parent / "data" / "portfolio_export.json"

    with open(data_path, "r") as f:
        portfolio = json.load(f)

    transactions = portfolio["transactions"]
    daily_prices = portfolio["dailyPrices"]

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

        grams = amount / price_per_gram if unit == "rupees" else amount

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


@mcp.tool()
def generate_ai_analysis() -> str:
    data_path = Path(__file__).parent / "data" / "portfolio_export.json"

    # reuse your own MCP tool logic
    summary = analyze_precious_metals()

    prompt = f"""
You are a professional financial advisor.

Portfolio Summary:
{summary}

Provide:
- Performance assessment
- Risk comment
- Strategic advice
- Confidence level
"""

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    return response.text


if __name__ == "__main__":
    print("MCP Server Started", file=sys.stderr)
    mcp.run()
