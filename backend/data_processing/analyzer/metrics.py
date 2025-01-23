import pandas as pd
import analyzer.default_classification_settings as default_classification_settings
DEFAULT_DISCRETIONARY_CATEGORIES = default_classification_settings.DEFAULT_DISCRETIONARY_CATEGORIES
DEFAULT_ESSENTIAL_CATEGORIES = default_classification_settings.DEFAULT_ESSENTIAL_CATEGORIES
DEFAULT_METRICS_DICTIONARY = default_classification_settings.DEFAULT_METRICS_DICTIONARY

DATA_LOSS_MESSAGES = {
    0: 'No data issues detected',
    1: "Some data is missing-a manual review of this applicant's data may be needed",
    2: "Significant data is missing-a manual review of this applicant's data is strongly recommended"
}

def _return_message_helper(data_loss_score, max_data_loss_score):
    if data_loss_score ==max_data_loss_score:
        return DATA_LOSS_MESSAGES[0]
    elif data_loss_score >= max_data_loss_score*.7:
        return DATA_LOSS_MESSAGES[1]
    else:
        return DATA_LOSS_MESSAGES[2]


def get_metrics_dictionary(**kwargs):
    """
    Instantiates a metrics dictionary based on DEFAULT_METRICS_DICTIONARY.
    Any keyword arguments provided that match keys in the default dictionary will override
    the default values.
    
    Returns:
      dict: A dictionary of weights for the loan eligibility score.
    """
    # Start with a copy of the default dictionary.
    weights = DEFAULT_METRICS_DICTIONARY.copy()
    # Update with any provided keyword arguments.
    for key, value in kwargs.items():
        if key in weights:
            weights[key] = value
    return weights

def aggregate_metrics(df, discretionary_categories = DEFAULT_DISCRETIONARY_CATEGORIES,
                       essential_categories = DEFAULT_ESSENTIAL_CATEGORIES ):
    """
    Given a DataFrame of transaction data, compute aggregation metrics useful for assessing an individual's loan eligibility.
    
    Expected columns in the DataFrame:
      - "Date": The transaction date.
      - "Debit": Expenses.
      - "Credit": Income.
      - "Balance": Account balance at the time of the transaction.
      - "Category": Transaction category (e.g., "Rent", "Salary", etc.).
      
    Returns:
      dict: A dictionary where keys are metric names and values are the computed values.
    """
    # Ensure DataFrame is sorted by date.
    
    metrics = {}
    
    # 1. Starting and Ending Balance.
    if not df.empty:
        starting_balance = df.iloc[0]["Balance"]
        ending_balance = df.iloc[-1]["Balance"]
    else:
        starting_balance = ending_balance = None
    metrics["starting_balance"] = starting_balance
    metrics["ending_balance"] = ending_balance

    # 2. Minimum Balance, Maximum Balance and its ratio to the starting balance.
    if not df.empty and "Balance" in df.columns:
        min_balance = df["Balance"].min()
        max_balance = df["Balance"].max()
    else:
        min_balance = None
        max_balance = None
    metrics["min_balance"] = min_balance
    metrics["max_balance"] = max_balance
    if starting_balance and starting_balance != 0:
        metrics["min_balance_ratio"] = min_balance / starting_balance
        metrics["max_balance_ratio"] = max_balance / starting_balance
    else:
        metrics["min_balance_ratio"] = None
        metrics["max_balance_ratio"] = None

    # 3. Total Income and Total Expenses.
    # Assume that deposits/income are in the "Credit" column and expenses in the "Debit" column.
    total_income = df["Credit"].dropna().sum() if "Credit" in df.columns else None
    total_expenses = df["Debit"].dropna().sum() if "Debit" in df.columns else None
    metrics["total_income"] = total_income
    metrics["total_expenses"] = total_expenses

    # 4. Category-Based Spending/Income.
    # Sum the debit/credit amounts grouped by category.
    if "Category" in df.columns:
        if "Debit" in df.columns:
            category_expenses = df.groupby("Category")["Debit"].sum().to_dict()
        else:
            category_expenses = {}
        metrics["category_expenses_debit"] = category_expenses

        if "Credit" in df.columns:
            category_expenses = df.groupby("Category")["Credit"].sum().to_dict()
        else:
            category_expenses = {}
        metrics["category_expenses_debit"] = category_expenses


    # If you want to compare essential spending vs discretionary spending,
    # you might pre-define lists of categories:
    
    essential_spending = sum(val for cat, val in category_expenses.items() if cat in essential_categories)
    discretionary_spending = sum(val for cat, val in category_expenses.items() if cat in discretionary_categories)
    metrics["essential_spending"] = essential_spending
    metrics["discretionary_spending"] = discretionary_spending

    # 5. Spending Variability.
    # Calculate standard deviation of Debit (expenses). Also compute the coefficient of variation (std / mean).
    if "Debit" in df.columns:
        debit_series = df["Debit"].dropna()
        spending_std = debit_series.std() if not debit_series.empty else None
        spending_mean = debit_series.mean() if not debit_series.empty else None
    else:
        spending_std = spending_mean = None
    metrics["spending_std"] = spending_std
    if spending_mean and spending_mean != 0:
        metrics["spending_cv"] = spending_std / spending_mean
    else:
        metrics["spending_cv"] = None

    # Compute net cash flow over the period (Total Income - Total Expenses)
    if total_income is not None and total_expenses is not None:
        metrics["net_cash_flow"] = total_income - total_expenses
    else:
        metrics["net_cash_flow"] = None
    
    return metrics

def calculate_loan_eligibility_score(metrics, weights=DEFAULT_METRICS_DICTIONARY):
    """
    Calculates a loan eligibility score based on key financial metrics using a provided dictionary of weights.
    
    Parameters:
      metrics (dict): A dictionary of metrics, e.g. as generated by aggregate_metrics().
      weights (dict): A dictionary specifying the weight for each metric component.
                      Default values are provided if not specified.
                      
    Returns:
      float: A loan eligibility score. Higher scores suggest stronger eligibility.
    """
    

    score = 0
    data_loss_warning = 0
    MAX_DATA_LOSS_SCORE=5

    # 1. Starting vs. Ending Balance.
    starting_balance = metrics.get("starting_balance")
    ending_balance = metrics.get("ending_balance")
    if starting_balance and ending_balance is not None:
        data_loss_warning+=1
        if ending_balance >= starting_balance:
            score += weights["balance_increase"]
        else:
            # Scale the points based on ratio.
            ratio = ending_balance / starting_balance if starting_balance != 0 else 0
            score += weights["balance_decrease"] * ratio
    
    # 2. Minimum Balance Ratio.
    min_balance_ratio = metrics.get("min_balance_ratio")
    if min_balance_ratio is not None:
        data_loss_warning+=1
        if min_balance_ratio >= 0.8:
            score += weights["min_balance_high"]
        elif min_balance_ratio >= 0.5:
            score += weights["min_balance_mid"]
        else:
            score += weights["min_balance_low"]
    
    # 3. Net Cash Flow.
    net_cash_flow = metrics.get("net_cash_flow")
    if net_cash_flow is not None:
        data_loss_warning+=1
        if net_cash_flow > 0:
            score += weights["positive_net"]
        else:
            score += weights["negative_net"]

    # 4. Essential Spending Ratio.
    total_expenses = metrics.get("total_expenses")
    essential_spending = metrics.get("essential_spending")
    if total_expenses and total_expenses > 0:
        data_loss_warning+=1
        essential_ratio = essential_spending / total_expenses
        if essential_ratio >= 0.7:
            score += weights["essential_high"]
        else:
            score += weights["essential_low"]
    
    # 5. Spending Variability.
    spending_cv = metrics.get("spending_cv")
    if spending_cv is not None:
        data_loss_warning+=1
        if spending_cv < 0.3:
            score += weights["low_variability"]
        elif spending_cv > 1.0:
            score += weights["high_variability"]
        # If spending_cv is between 0.3 and 1.0, we add 0 points.
    
    return_message = _return_message_helper(data_loss_score=data_loss_warning, max_data_loss_score=MAX_DATA_LOSS_SCORE)


    return score, return_message
