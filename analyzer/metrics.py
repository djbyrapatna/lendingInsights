import pandas as pd
import analyzer.default_classification_settings as default_classification_settings
DEFAULT_DISCRETIONARY_CATEGORIES = default_classification_settings.DEFAULT_DISCRETIONARY_CATEGORIES
DEFAULT_ESSENTIAL_CATEGORIES = default_classification_settings.DEFAULT_ESSENTIAL_CATEGORIES

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
