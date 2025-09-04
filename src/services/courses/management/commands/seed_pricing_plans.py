from django.core.management.base import BaseCommand
from src.services.courses.models import PricingPlan


class Command(BaseCommand):
    help = 'Seed the database with sample pricing plans'

    def handle(self, *args, **options):
        self.stdout.write('Creating pricing plans...')
        
        # Clear existing pricing plans
        PricingPlan.objects.all().delete()
        
        # Create pricing plans
        from decimal import Decimal
        plans_data = [
            {
                'name': '2 Days Per Week',
                'price': Decimal('25.00'),
                'currency': 'USD',
                'billing_period': 'monthly',
                'classes_per_week': 2,
                'classes_per_month': 8,
                'students_enrolled': 1500,
                'is_popular': False,
                'six_month_discount': 7,
                'twelve_month_discount': 10,
            },
            {
                'name': '3 Days Per Week',
                'price': Decimal('35.00'),
                'currency': 'USD',
                'billing_period': 'monthly',
                'classes_per_week': 3,
                'classes_per_month': 12,
                'students_enrolled': 2500,
                'is_popular': True,
                'six_month_discount': 7,
                'twelve_month_discount': 10,
            },
            {
                'name': '4 Days Per Week',
                'price': Decimal('45.00'),
                'currency': 'USD',
                'billing_period': 'monthly',
                'classes_per_week': 4,
                'classes_per_month': 16,
                'students_enrolled': 3500,
                'is_popular': False,
                'six_month_discount': 7,
                'twelve_month_discount': 10,
            },
            {
                'name': '5 Days Per Week',
                'price': Decimal('55.00'),
                'currency': 'USD',
                'billing_period': 'monthly',
                'classes_per_week': 5,
                'classes_per_month': 20,
                'students_enrolled': 4500,
                'is_popular': False,
                'six_month_discount': 7,
                'twelve_month_discount': 10,
            },
            {
                'name': 'Weekend Classes',
                'price': Decimal('30.00'),
                'currency': 'USD',
                'billing_period': 'monthly',
                'classes_per_week': 2,
                'classes_per_month': 8,
                'students_enrolled': 2000,
                'is_popular': False,
                'six_month_discount': 7,
                'twelve_month_discount': 10,
            },
        ]
        
        created_plans = []
        for plan_data in plans_data:
            plan = PricingPlan.objects.create(**plan_data)
            created_plans.append(plan)
            self.stdout.write(f'Created pricing plan: {plan.name} - ${plan.price}/{plan.billing_period}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(created_plans)} pricing plans!')
        )
        
        # Display summary
        self.stdout.write('\nPricing Plans Summary:')
        self.stdout.write('=' * 50)
        for plan in created_plans:
            self.stdout.write(f'{plan.name}:')
            self.stdout.write(f'  Monthly: ${plan.price}')
            self.stdout.write(f'  6 Months: ${plan.get_six_month_price():.2f} (Save {plan.six_month_discount}%)')
            self.stdout.write(f'  12 Months: ${plan.get_twelve_month_price():.2f} (Save {plan.twelve_month_discount}%)')
            self.stdout.write(f'  Classes: {plan.classes_per_week}/week, {plan.classes_per_month}/month')
            self.stdout.write('')
