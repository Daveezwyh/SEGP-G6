import pandas as pd
import json
import os
from dotenv import load_dotenv
from api.models import Cleaner

load_dotenv()

class CleanerSeeder:
    def __init__(self):
        self.file_path = os.getenv("CLEANER_FILE", "../cleaners.xlsx")

    def seed(self):
        print(f'\nSeeding Cleaners...')

        if not os.path.exists(self.file_path):
            print(f"\033[91mCleaner file not found: {self.file_path}\033[0m\n")
            return
        
        try:
            df = pd.read_excel(self.file_path, engine="openpyxl")

            for _, row in df.iterrows():
                fn_name = row["fn_name"]

                cleaner, created = Cleaner.objects.get_or_create(fn_name=fn_name)

                cleaner.name = row["name"]
                cleaner.description = row["description"]
                cleaner.status = row["status"] if not pd.isna(row["status"]) else 0
                cleaner.definition = row["definition"]

                cleaner.save()

                action = "Created" if created else "Updated"
                #print(f"{action} Cleaner: {fn_name}")

        except Exception as e:
            print(f"\033[91mError: {e}\033[0m")
        
        print(f'Cleaners seeded successfully.\n')