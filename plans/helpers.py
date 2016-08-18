import time

def get_response_plan_list(plans):
    return [{"id": i.id,
             "name": i.name,
             "currency": i.currency,
             "amount": i.amount,
             "interval": i.interval,
             "interval_count": i.interval_count,
             "trial_period_days": i.trial_period_days} for i in plans]

def filtering_plan_by_currency(plans, currency):
    return [plan for plan in plans if plan['currency'] == currency]

def reject_free_plans(plans):
    return [plan for plan in plans if plan['trial_period_days'] is None]

def get_response_invoice_list(invoices):
    return [invoice.__dict__['_previous'] for invoice in invoices]

def get_timestamp_from_datetime(datetime):
    return int(time.mktime(datetime.timetuple()))
