DEFAULT_CLASSIFICATION_MODEL = "valhalla/distilbart-mnli-12-3"
DEFAULT_CANDIDATE_LABELS = ["Rent", "Salary", "Utilities", "Bill payment", "Transfer", "Entertainment", "Food", "Medical", "Other Bills", "Other"]
DEFAULT_CONTEXT = 'These are bank transaction statements: '
DEFAULT_DISCRETIONARY_CATEGORIES = {"Food", "Medical", "Entertainment"}
DEFAULT_EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
DEFAULT_ESSENTIAL_CATEGORIES = {"Rent", "Utilities", "Bill Payment"}

DEFAULT_METRICS_DICTIONARY = {
    "balance_increase": 20,   # if ending_balance >= starting_balance
    "balance_decrease": 10,   # if ending_balance < starting_balance (scaled by ratio)
    "min_balance_high": 20,   # if min_balance_ratio >= 0.8
    "min_balance_mid": 10,    # if 0.5 <= min_balance_ratio < 0.8
    "min_balance_low": -10,   # if min_balance_ratio < 0.5
    "positive_net": 15,       # if net_cash_flow > 0
    "negative_net": -10,      # if net_cash_flow <= 0
    "essential_high": 15,     # if essential spending ratio >= 0.7
    "essential_low": -5,      # if essential spending ratio < 0.7
    "low_variability": 10,    # if spending_cv < 0.3
    "high_variability": -10   # if spending_cv > 1.0
}


