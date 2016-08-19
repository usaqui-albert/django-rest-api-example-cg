import time

# Helper functions for Plan services
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

def filter_free_plans(plans):
    return [plan for plan in plans if plan['trial_period_days']]

# Helper functions for Invoice services
def get_response_invoice_list(invoices, email):
    invoice_list = []
    for invoice in invoices:
        invoice_dict = filtering_dict_by_keys(invoice.__dict__['_previous'], _list)
        invoice_dict['email'] = email
        invoice_dict['lines'] = customize_invoice_lines(invoice_dict['lines'])
        invoice_list.append(invoice_dict)
    return invoice_list

def customize_invoice_lines(lines):
    return [filtering_dict_by_keys(i, _list_line_) for i in lines['data']]

# Helper miscellaneous functions
def get_timestamp_from_datetime(datetime):
    return int(time.mktime(datetime.timetuple()))

def filtering_dict_by_keys(dic, key_list):
    return dict((key, value) for key, value in dic.iteritems() if key in key_list)

_list = ['total', 'subtotal', 'lines', 'paid', 'period_end', 'period_start', 'tax',
         'tax_percent', 'currency', 'date', 'id', 'application_fee'
         ]
_list_line_ = ['plan', 'period', 'currency', 'amount']
