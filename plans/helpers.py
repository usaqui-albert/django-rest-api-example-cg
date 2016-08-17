def get_response_plan_list(plans):
    return [{"id": i.id,
             "name": i.name,
             "currency": i.currency,
             "amount": i.amount,
             "interval": i.interval,
             "trial_period_days": i.trial_period_days} for i in plans]

def filtering_plan_by_currency(plans, currency):
    return [plan for plan in plans if plan['currency'] == currency]

def reject_free_plans(plans):
    return [plan for plan in plans if plan['trial_period_days'] is None]
