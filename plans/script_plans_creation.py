"""Script to create tests plans in stripe"""

import stripe
from ConnectGood.settings import STRIPE_API_KEY

stripe.api_key = STRIPE_API_KEY

stripe.Plan.create(amount=10, interval='month', name='Test Monthly Plan US',
                   currency='usd', id='monthUs')

stripe.Plan.create(amount=100, interval='year', name='Test Yearly Plan US',
                   currency='usd', id='yearUs')

stripe.Plan.create(amount=13, interval='month', name='Test Monthly Plan Canadian',
                   currency='cad', id='monthCad')

stripe.Plan.create(amount=130, interval='year', name='Test Yearly Plan Canadian',
                   currency='cad', id='yearCad')
