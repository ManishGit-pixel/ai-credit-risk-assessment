import random

def fetch_user_data(user_id: str) -> dict:
    """
    Simulate fetching enhanced financial and behavioral user data from internal systems.
    In a real system, this would query a database or external APIs (like credit bureaus).
    """
    # Mocking some external data points that could be useful or exist
    return {
        "user_id": user_id,
        "past_defaults": random.choice([0, 0, 1]), # 33% chance of a past default
        "num_active_credit_lines": random.randint(1, 10),
        "bank_balance_average": random.uniform(500.0, 50000.0)
    }
