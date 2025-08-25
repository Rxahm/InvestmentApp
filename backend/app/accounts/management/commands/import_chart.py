import pandas as pd
import os
from django.core.management.base import BaseCommand
from app.accounts.models import Account

class Command(BaseCommand):
    help = 'Import chart of accounts from Excel file'

    def handle(self, *args, **kwargs):
        try:
            # Go up 2 directories: backend/app/accounts -> backend -> PretiumInvestmentApp
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            file_path = os.path.join(base_dir, 'chart_of_accounts.xlsx')

            # Load Excel file
            df = pd.read_excel(file_path)

            # Insert accounts
            for index, row in df.iterrows():
                account, created = Account.objects.get_or_create(
                    code=row['code'],
                    defaults={
                        'name': row['name'],
                        'type': row['type'],
                        'description': row.get('description', ''),
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"✅ Created Account: {account.name}"))
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Account already exists: {account.name}"))

            self.stdout.write(self.style.SUCCESS('🎯 Chart of Accounts imported successfully!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error importing Chart of Accounts: {str(e)}"))
