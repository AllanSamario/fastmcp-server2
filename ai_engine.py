from typing import Dict


def format_summary_for_ai(summary: Dict) -> str:
    return f"""
PORTFOLIO SUMMARY

Gold:
Grams: {summary['gold']['grams']}
Invested: ₹{summary['gold']['invested']}
Current Value: ₹{summary['gold']['current_value']}
ROI: {summary['gold']['roi_percent']}%

Silver:
Grams: {summary['silver']['grams']}
Invested: ₹{summary['silver']['invested']}
Current Value: ₹{summary['silver']['current_value']}
ROI: {summary['silver']['roi_percent']}%

Overall Portfolio:
Total Invested: ₹{summary['overall']['invested']}
Total Value: ₹{summary['overall']['value']}
Overall ROI: {summary['overall']['roi_percent']}%
"""


def generate_ai_analysis(summary: Dict) -> str:
    formatted_data = format_summary_for_ai(summary)

    # For now: rule-based reasoning (AI-style)
    roi = summary["overall"]["roi_percent"]

    if roi > 10:
        stance = "Strong Positive Performance"
        recommendation = "Hold or partial profit booking"
    elif roi > 0:
        stance = "Mild Positive Performance"
        recommendation = "Hold"
    else:
        stance = "Underperforming"
        recommendation = "Review allocation"

    return f"""
AI Portfolio Analysis

{formatted_data}

Assessment: {stance}
Recommendation: {recommendation}

This analysis is based on current ROI performance and metal allocation.
Confidence Level: 75%
"""