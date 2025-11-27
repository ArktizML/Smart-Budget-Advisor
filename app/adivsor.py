import statistics
from datetime import datetime
from collections import defaultdict

def analyze_expenses(expenses):
    if not expenses:
        return{
            "category_shares": {},
            "monthly_trend": None,
            "daily_avg": None,
            "daily_median": None,
            "anomalies": [],
            "insights": ["No expenses. Add some expenses, then I will generate the raport."]
                            }
    
    total = sum(e["amount"] for e in expenses)

    categories = defaultdict(float)
    for e in expenses:
        categories[e["category"]] += e["amount"]

    category_shares = {
        cat: round(val / total, 4)
        for cat, val in categories.items()
    }

    amounts = [e["amount"] for e in expenses]
    daily_avg = round(sum(amounts) / len(amounts), 2)
    daily_median = round(statistics.median(amounts), 2)

    by_month = defaultdict(float)
    for e in expenses:
        dt = datetime.strptime(e["date"], "%Y-%m-%d %H:%M:%S")
        key = f"{dt.year}-{dt.month:02d}"
        by_month[key] += e["amount"]

    sorted_months = sorted(by_month.keys())
    monthly_trend = None

    if len(sorted_months) >= 2:
        prev, curr = sorted_months[-2], sorted_months[-1]
        p, c = by_month[prev], by_month[curr]
        if p > 0:
            monthly_trend = round((c - p) / p, 3)
        else:
            monthly_trend = None

    anomalies = []
    for e in expenses:
        if e["amount"] > daily_median * 2:
            anomalies.append({
                "amount": e["amount"],
                "category": e["category"],
                "date": e["date"]
            })

    insights =  generate_insights(category_shares, monthly_trend, daily_avg, daily_median, anomalies)

    return {
        "category_shares": category_shares,
        "monthly_trend": monthly_trend,
        "daily_avg": daily_avg,
        "daily_median": daily_median,
        "anomalies": anomalies,
        "insights": insights
    }

def generate_insights(category_shares, monthly_trend, daily_avg, daily_median, anomalies):
    insights = [] 
    
    for category, share in category_shares.items():
        if category.lower() in ["food"] and share > 0.35:
            insights.append("Food expenses exceed 35%. Try meal planning or shopping with a list.")

        if category.lower() in ["transport"] and share > 0.20:
            insights.append("Transport costs exceed 20% of the budget. Consider optimizing your route or using cheaper fuel.")

    if monthly_trend is not None:
        if monthly_trend > 0.15:
            insights.append(f"Expenses are increasing by  {monthly_trend*100:.1f}%. It is worth reviewing where the budget has been spent.")

        if monthly_trend < -0.10:
            insights.append("Great! Expenses have decreased by over 10% compared to the previous month.")

    if daily_avg > daily_median * 1.2:
        insights.append("Your average daily spending is unusually high. You probably have a few large transactions pulling your budget up.")

    if anomalies:
        insights.append("Unusual expenses have been detected – check whether they were necessary.")

    if not insights:
        insights.append("Your expenses look stable. Good job.")

    return insights