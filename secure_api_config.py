#!/usr/bin/env python3
"""
Secure API Configuration for Trading Bots
"""

# Kraken API Credentials
KRAKEN_API_KEY = "9hYXpC21eznbgcPpvYdYV0Nc4tGNy6Iz30aU31ysauVApafXJOBHjq14"
KRAKEN_API_SECRET = "JqcHH3iSaj0SYQyPp74uqhfuKLXAfeypBnX0drjC0YyrP+RVjp3eRgWVtpFfLKiWKjHVQak/VWyKQbZkr5QR5Q=="

# Risk Management Settings
RISK_SETTINGS = {
    "low": {"capital": 1500, "max_trade": 30, "max_loss": 100},
    "med": {"capital": 3000, "max_trade": 60, "max_loss": 100},
    "high": {"capital": 5000, "max_trade": 100, "max_loss": 100}
}

def get_kraken_credentials():
    return KRAKEN_API_KEY, KRAKEN_API_SECRET
