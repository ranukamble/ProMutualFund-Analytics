import numpy as np

def calculate_portfolio_metrics(funds, allocation, investment_details):
    """
    funds: list of fund data dicts (from mutual fund API/DB)
    allocation: dict mapping fund code to weight (0-100)
    investment_details: dict with sip_amount, lumpsum_amount, horizon, etc.
    """
    total_weight = sum(allocation.values())
    if total_weight != 100:
        return {"error": f"Total allocation must be 100%. Current is {total_weight}%"}

    # Initialize aggregators
    equity_weight = 0
    debt_weight = 0
    hybrid_weight = 0
    gold_weight = 0
    
    weighted_expense_ratio = 0
    weighted_1y = 0
    weighted_3y = 0
    weighted_5y = 0
    
    amc_allocation = {}
    category_allocation = {}
    
    for fund in funds:
        code = str(fund.get('code'))
        weight = allocation.get(code, 0)
        weight_frac = weight / 100.0
        
        # Determine category
        cat = str(fund.get('category', 'Other')).lower()
        if 'equity' in cat:
            equity_weight += weight
        elif 'debt' in cat:
            debt_weight += weight
        elif 'hybrid' in cat or 'balanced' in cat:
            hybrid_weight += weight
        elif 'gold' in cat:
            gold_weight += weight
        else:
            equity_weight += weight # Default fallback for simplicity
            
        # Expenses
        er = fund.get('expense_ratio', 0) or 0
        weighted_expense_ratio += (float(er) * weight_frac)
        
        # Returns
        r1 = fund.get('returns_1yr', 0) or 0
        r3 = fund.get('returns_3yr', 0) or 0
        r5 = fund.get('returns_5yr', 0) or 0
        weighted_1y += (float(r1) * weight_frac)
        weighted_3y += (float(r3) * weight_frac)
        weighted_5y += (float(r5) * weight_frac)
        
        # AMC
        amc = fund.get('amc', 'Unknown AMC')
        amc_allocation[amc] = amc_allocation.get(amc, 0) + weight
        
        # Category Breakdown
        category_allocation[cat] = category_allocation.get(cat, 0) + weight
        
    # SIP Projection
    sip = float(investment_details.get('sip_amount', 0))
    lumpsum = float(investment_details.get('lumpsum_amount', 0))
    horizon_years = float(investment_details.get('horizon', 5))
    expected_return = float(investment_details.get('expected_return', weighted_3y if weighted_3y > 0 else 12))
    
    months = horizon_years * 12
    monthly_rate = (expected_return / 100) / 12
    
    # Future Value of SIP
    sip_fv = 0
    if monthly_rate > 0 and sip > 0:
        sip_fv = sip * (((1 + monthly_rate)**months - 1) / monthly_rate) * (1 + monthly_rate)
    elif sip > 0:
        sip_fv = sip * months
        
    # Future Value of Lumpsum
    lumpsum_fv = 0
    if lumpsum > 0:
        lumpsum_fv = lumpsum * ((1 + (expected_return / 100)) ** horizon_years)
        
    total_invested = (sip * months) + lumpsum
    projected_value = sip_fv + lumpsum_fv
    estimated_gain = projected_value - total_invested

    return {
        "status": "success",
        "allocation": {
            "equity": round(equity_weight, 2),
            "debt": round(debt_weight, 2),
            "hybrid": round(hybrid_weight, 2),
            "gold": round(gold_weight, 2)
        },
        "performance": {
            "returns_1yr": round(weighted_1y, 2),
            "returns_3yr": round(weighted_3y, 2),
            "returns_5yr": round(weighted_5y, 2)
        },
        "cost": {
            "weighted_expense_ratio": round(weighted_expense_ratio, 2)
        },
        "diversification": {
            "amc_allocation": amc_allocation,
            "category_allocation": category_allocation,
            "total_funds": len(funds),
            "total_amcs": len(amc_allocation)
        },
        "projection": {
            "total_invested": round(total_invested, 2),
            "projected_value": round(projected_value, 2),
            "estimated_gain": round(estimated_gain, 2),
            "expected_return_used": round(expected_return, 2)
        }
    }
