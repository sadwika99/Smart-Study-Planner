def optimize_study_plan(subjects, total_time_available):
    """
    Advanced Optimization System:
    Step 1: 0/1 Knapsack (DP) for optimal core selection.
    Step 2: Smart Fill (Greedy) for remaining time utilization.
    """
    n = len(subjects)
    W = total_time_available
    
    # DP Table
    dp = [[0 for _ in range(W + 1)] for _ in range(n + 1)]
    
    for i in range(1, n + 1):
        item = subjects[i-1]
        weight = item['study_time']
        value = item['importance']
        for w in range(W + 1):
            if weight <= w:
                dp[i][w] = max(value + dp[i-1][w-weight], dp[i-1][w])
            else:
                dp[i][w] = dp[i-1][w]
    
    # Backtrack for Optimal Selection (DP)
    dp_selected = []
    unselected_candidates = []
    w = W
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i-1][w]:
            item = subjects[i-1]
            dp_selected.append(item)
            w -= item['study_time']
        else:
            unselected_candidates.append(subjects[i-1])
            
    # Step 3: Smart Fill (Greedy Addition)
    # Sort remaining by efficiency (value/weight)
    unselected_candidates.sort(key=lambda x: x['importance'] / x['study_time'] if x['study_time'] > 0 else 0, reverse=True)
    
    added_subjects = []
    remaining_time = w
    
    for item in unselected_candidates:
        if item['study_time'] <= remaining_time:
            added_subjects.append(item)
            remaining_time -= item['study_time']
            
    # Calculate totals
    total_score = dp[n][W] + sum(item['importance'] for item in added_subjects)
    total_time_used = total_time_available - remaining_time
    
    # Identify rejected subjects
    added_names = [s['name'] for s in added_subjects]
    rejected_subjects = [s for s in unselected_candidates if s['name'] not in added_names]
    
    return {
        "dp_selected": dp_selected[::-1],
        "added_subjects": added_subjects,
        "rejected_subjects": rejected_subjects,
        "total_score": total_score,
        "used_time": total_time_used,
        "remaining_time": remaining_time,
        "available_time": total_time_available
    }
