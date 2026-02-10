import pandas as pd  # type: ignore

class BadgeManager:
    def __init__(self):
        self.badges = [
            {
                "id": "savings_hero",
                "name": "Savings Hero",
                "icon": "🔥",
                "description": "Saved more than 25% of income",
                "condition": lambda details: details.get('savings_ratio', 0) >= 25
            },
            {
                "id": "wealth_builder",
                "name": "Wealth Builder",
                "icon": "💎",
                "description": "Invested more than 20% of income",
                "condition": lambda details: details.get('investment_ratio', 0) >= 20
            },
            {
                "id": "budget_master",
                "name": "Budget Master",
                "icon": "🛡️",
                "description": "Kept Needs under 50% of income",
                "condition": lambda details: details.get('needs_ratio', 0) > 0 and details.get('needs_ratio', 0) <= 50
            },
            {
                "id": "data_wizard",
                "name": "Data Wizard",
                "icon": "🧠",
                "description": "Uploaded data for more than 3 months",
                "condition": lambda details: details.get('month_count', 0) >= 3
            }
        ]
        
    def check_badges(self, df, health_details):
        """
        Check which badges the user has earned.
        health_details: dict returned from calculate_financial_health_score
        """
        earned = []
        
        # Augment details with data-specifics
        if df is not None:
             if 'date' in df.columns:
                 try:
                     # Ensure date is datetime
                     temp_dates = pd.to_datetime(df['date'], errors='coerce')
                     month_count = temp_dates.dt.to_period('M').nunique()
                     health_details['month_count'] = month_count
                 except Exception:
                     health_details['month_count'] = 0
        
        # Check conditions
        for badge in self.badges:
            try:
                if badge['condition'](health_details):  # type: ignore
                    earned.append(badge)
            except:
                pass
                
        return earned
