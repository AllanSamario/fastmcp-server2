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

# --- THE UNIVERSAL MATH ENGINE ---
def run_portfolio_calculation(portfolio: PortfolioFile) -> str:
    """
    Shared logic to calculate grams and value from a PortfolioFile object.
    Ensures consistency between local file analysis and live AI analysis.
    """
    def process_metal(data: MetalData) -> Dict[str, Any]:
        if not data.get("dailyPrices") or not data.get("transactions"):
            return {"grams": 0.0, "value": 0.0, "price": 0.0}
        
        # Get latest price
        latest: DailyPrice = max(data["dailyPrices"], key=lambda x: x["date"])
        price_now: float = float(latest["pricePerGram"])
        
        total_grams: float = 0.0
        for t in data["transactions"]:
            t_price: float = float(t.get("pricePerGram", price_now))
            amount: float = float(t["amount"])
            
            # Logic: If unit is rupees, convert to grams
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

    gold = process_metal(portfolio["gold"])
    silver = process_metal(portfolio["silver"])
    total_val = gold["value"] + silver["value"]

    return f"""
📊 Portfolio Stats:
Total Portfolio Value: ₹{total_val:,.2f}

Gold:
- Total Grams: {gold['grams']:.2f}g
- Current Value: ₹{gold['value']:,.2f}

Silver:
- Total Grams: {silver['grams']:.2f}g
- Current Value: ₹{silver['value']:,.2f}
"""

@mcp.tool()
def analyze_precious_metals() -> str:
    """Standard Tool: Processes the local 'portfolio_export.json' file."""
    base_dir: Path = Path(__file__).resolve().parent
    data_path: Path = base_dir / "data" / "portfolio_export.json"

    if not data_path.exists():
        return f"Error: Portfolio data file not found at {data_path}."

    with open(data_path, "r") as f:
        portfolio: PortfolioFile = json.load(f)
    
    return run_portfolio_calculation(portfolio)

@mcp.tool()
def generate_ai_analysis(portfolio_data: Optional[str] = None, question: str = "General Analysis") -> str:
    """
    AI Tool: Accepts live JSON from the app (portfolio_data).
    If none is provided, it falls back to the local file.
    """
    # 1. Get the Context (Math)
    if portfolio_data:
        try:
            live_portfolio: PortfolioFile = json.loads(portfolio_data)
            summary = run_portfolio_calculation(live_portfolio)
        except Exception as e:
            return f"Error parsing live data: {str(e)}"
    else:
        summary = analyze_precious_metals()

    # 2. Get AI Advice
    client = get_ai_client()
    if not client:
        return "Error: GEMINI_API_KEY environment variable not set."

    prompt: str = f"""
    You are a professional financial advisor.
    Current Portfolio Snapshot: {summary}
    User Question: {question}

    Provide a performance assessment, risk comment, and strategic advice.
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text if response.text else "AI Analysis failed."
    except Exception as e:
        return f"Gemini Error: {str(e)}"

if __name__ == "__main__":
    print("Precious Metals MCP Server initializing...", file=sys.stderr)
    mcp.run()
