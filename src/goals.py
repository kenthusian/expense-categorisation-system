import pandas as pd
import os
from datetime import datetime

GOALS_FILE = "goals.csv"

class GoalManager:
    def __init__(self, goals_file=GOALS_FILE):
        self.goals_file = goals_file
        self.goals = self.load_goals()

    def load_goals(self):
        if os.path.exists(self.goals_file):
            try:
                return pd.read_csv(self.goals_file)
            except Exception:
                return pd.DataFrame(columns=["name", "target_amount", "saved_amount", "target_date"])
        else:
            return pd.DataFrame(columns=["name", "target_amount", "saved_amount", "target_date"])

    def save_goals(self):
        self.goals.to_csv(self.goals_file, index=False)

    def add_goal(self, name, target_amount, saved_amount, target_date):
        new_row = pd.DataFrame({
            "name": [name],
            "target_amount": [target_amount],
            "saved_amount": [saved_amount],
            "target_date": [target_date]
        })
        self.goals = pd.concat([self.goals, new_row], ignore_index=True)
        self.save_goals()

    def update_goal(self, index, saved_amount):
        if 0 <= index < len(self.goals):
            self.goals.at[index, "saved_amount"] = saved_amount
            self.save_goals()
            return True
        return False

    def delete_goal(self, index):
        if 0 <= index < len(self.goals):
            self.goals = self.goals.drop(index).reset_index(drop=True)
            self.save_goals()
            return True
        return False

    def get_goals(self):
        return self.goals
