import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from fastmcp import FastMCP
from google import genai

# 🔥 IMPORT YOUR MODELS HERE
from models import PortfolioFile, MetalData, DailyPrice

mcp = FastMCP("Precious Metals Portfolio AI")

def get_ai_client() -> Optional[genai.Client]:
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    return genai.Client(api_key=api_key) if api_key else None

@mcp.tool()
def analyze_precious_metals() -> str:
    """Calculates portfolio stats using the TypedDict structure from models.py."""
    data_path: Path = Path(__file__).parent / "data" / "portfolio_export.json"

    if not data_path.exists():
        return "Error: Data file not found."

    with open(data_path, "r") as f:
        # Cast the JSON data to your PortfolioFile type
        portfolio: PortfolioFile = json.load(f)

    def process_metal(name: str, data: MetalData) -> Dict[str, Any]:
        if not data["dailyPrices"]:
            return {"grams": 0, "value": 0, "price": 0}
        
        latest: DailyPrice = max(data["dailyPrices"], key=lambda x: x["date"])
        price_now = latest["pricePerGram"]
        
        total_grams = 0.0
        for t in data["transactions"]:
            grams = t["amount"] / t["pricePerGram"] if t["unit"] == "rupees" else t["amount"]
            total_grams += grams if t["type"] == "buy" else -grams
            
        return {
            "grams": total_grams,
            "price": price_now,
            "value": total_grams * price_now
        }

    gold = process_metal("Gold", portfolio["gold"])
    silver = process_metal("Silver", portfolio["silver"])
    total_val = gold["value"] + silver["value"]

    return f"""
📊 Portfolio Analysis (via models.py)
Total Value: ₹{total_val:,.2f}

Gold: {gold['grams']:.2f}g | Value: ₹{gold['value']:,.2f}
Silver: {silver['grams']:.2f}g | Value: ₹{silver['value']:,.2f}
"""

@mcp.tool()
def generate_ai_analysis() -> str:
    """Provides professional AI assessment using Gemini 2.0 Flash."""
    summary: str = analyze_precious_metals()
    client = get_ai_client()
    
    if not client:
        return "Error: GEMINI_API_KEY not set."

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"Analyze this precious metals portfolio:\n{summary}"
    )
    return response.text if response.text else "AI Analysis failed."

if __name__ == "__main__":
    mcp.run()