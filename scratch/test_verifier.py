with open('templates/verifier.html', 'r', encoding='utf-8') as f:
    content = f.read()

ids_to_check = [
    'scoreValue', 'scoreBar', 'exactMatchCount', 'discrepancyCount', 
    'outdatedCount', 'comparisonTableBody', 'emptyStateContainer', 
    'singleFundContent', 'schemeTitle', 'fundHouseDisplay', 
    'categoryDisplay', 'codeDisplay', 'isinDisplay', 'activeCodeLabel', 
    'lastAuditTime', 'schemeInput', 'fundSearchInput', 'searchResultsDropdown'
]

for x in ids_to_check:
    target1 = f'id="{x}"'
    target2 = f"id='{x}'"
    found = target1 in content or target2 in content
    print(f'{x}: {"FOUND" if found else "MISSING!"}')

