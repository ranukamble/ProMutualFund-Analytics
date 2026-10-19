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
    weighted_returns = {y: 0.0 for y in range(1, 11)}
    
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
        
        # Returns for all individual years 1 to 10
        for y in range(1, 11):
            ry = fund.get(f'returns_{y}yr', fund.get(f'return_{y}yr', fund.get(f'ret{y}y', 0))) or 0
            if isinstance(ry, str):
                ry = ry.replace('%', '').replace('+', '').strip()
                try:
                    ry = float(ry)
                except ValueError:
                    ry = 0
            weighted_returns[y] += (float(ry) * weight_frac)
        
        # AMC
        amc = fund.get('amc', 'Unknown AMC')
        amc_allocation[amc] = amc_allocation.get(amc, 0) + weight
        
        # Category Breakdown
        category_allocation[cat] = category_allocation.get(cat, 0) + weight
        
    # SIP Projection
    sip = float(investment_details.get('sip_amount', 0))
    lumpsum = float(investment_details.get('lumpsum_amount', 0))
    horizon_years = float(investment_details.get('horizon', 5))
    expected_return = float(investment_details.get('expected_return', weighted_returns[3] if weighted_returns[3] > 0 else 12))
    
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
            **{f"returns_{y}yr": round(weighted_returns[y], 2) for y in range(1, 11)}
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
