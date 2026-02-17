import sys
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from fastmcp import FastMCP
from google import genai

# 🔥 IMPORT YOUR MODELS
# Ensure models.py and __init__.py are in the same directory
from models import PortfolioFile, MetalData, DailyPrice

# Initialize FastMCP Server
mcp = FastMCP("Precious Metals Portfolio AI")

def get_ai_client() -> Optional[genai.Client]:
    """Safely retrieves the Gemini client using environment variables."""
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

@mcp.tool()
def analyze_precious_metals() -> str:
    """
    Calculates portfolio statistics (Grams, Current Price, Value) 
    using the TypedDict structure from models.py.
    """
    # Use absolute path resolution for Horizon cloud compatibility
    base_dir: Path = Path(__file__).resolve().parent
    data_path: Path = base_dir / "data" / "portfolio_export.json"

    if not data_path.exists():
        return f"Error: Portfolio data file not found at {data_path}."

    try:
        with open(data_path, "r") as f:
            # Cast the JSON data to your PortfolioFile type
            portfolio: PortfolioFile = json.load(f)

        def process_metal(name: str, data: MetalData) -> Dict[str, Any]:
            """Helper logic to process specific metal transactions."""
            if not data.get("dailyPrices") or not data.get("transactions"):
                return {"grams": 0.0, "value": 0.0, "price": 0.0}
            
            # Find the latest price entry
            latest: DailyPrice = max(data["dailyPrices"], key=lambda x: x["date"])
            price_now: float = float(latest["pricePerGram"])
            
            total_grams: float = 0.0
            for t in data["transactions"]:
                # Logic: If unit is rupees, convert to grams using the transaction-time price
                # Ensure we handle strings/floats from JSON safely
                t_price: float = float(t.get("pricePerGram", price_now))
                amount: float = float(t["amount"])
                
                grams: float = amount / t_price if t["unit"] == "rupees" else amount
                
                if t["type"] == "buy":
                    total_grams += grams
                else:
                    total_grams -= grams
                
            return {
                "grams": total_grams,
                "price": price_now,
                "value": total_grams * price_now
            }

        # Process the nested structure defined in models.py
        gold: Dict[str, Any] = process_metal("Gold", portfolio["gold"])
        silver: Dict[str, Any] = process_metal("Silver", portfolio["silver"])
        total_val: float = gold["value"] + silver["value"]

        return f"""
📊 Portfolio Analysis (via models.py)
Total Portfolio Value: ₹{total_val:,.2f}

Gold:
- Total Grams: {gold['grams']:.2f}g
- Current Price: ₹{gold['price']:,.2f}/g
- Current Value: ₹{gold['value']:,.2f}

Silver:
- Total Grams: {silver['grams']:.2f}g
- Current Price: ₹{silver['price']:,.2f}/g
- Current Value: ₹{silver_stats['value']:,.2f}
"""
    except Exception as e:
        return f"Error processing portfolio: {str(e)}"

@mcp.tool()
def generate_ai_analysis() -> str:
    """
    Generates a professional financial assessment using Gemini 2.0 Flash 
    based on the current portfolio data.
    """
    # 1. Get current stats from our primary tool
    summary: str = analyze_precious_metals()
    
    # 2. Setup Gemini Client
    client: Optional[genai.Client] = get_ai_client()
    if not client:
        return "Error: GEMINI_API_KEY environment variable is not set in Horizon."

    # 3. Request Analysis
    prompt: str = (
        "You are a professional financial advisor specializing in physical commodities. "
        f"Analyze this precious metals portfolio summary and provide a performance assessment, "
        f"risk comment, and strategic advice:\n\n{summary}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text if response.text else "AI Analysis failed to generate text."
    except Exception as e:
        return f"Gemini API Error: {str(e)}"

if __name__ == "__main__":
    # stderr helps Horizon's logs stay clean
    print("Precious Metals MCP Server initializing...", file=sys.stderr)
    mcp.run()