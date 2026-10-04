def build_params(start_date, end_date, states, categories, all_states, all_categories):
    use_state = 0 if not states else 1
    use_cat = 0 if not categories else 1
    return {
        "start_date": start_date, "end_date": end_date,
        "use_state": use_state, "states": states or [""],
        "use_cat": use_cat, "categories": categories or [""],
    }