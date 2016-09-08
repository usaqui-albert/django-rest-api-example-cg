import time

# Helper functions for Plan services
plan_filter_keys = ['id', 'name', 'currency', 'amount', 'interval', 'interval_count',
                    'trial_period_days']

def get_plans_list_response(plans):
    """Function to filter the format plan received from stripe by the required keys"""
    return [filtering_dict_by_keys(plan, plan_filter_keys) for plan in plans]

def filtering_plan_by_currency(plans, currency):
    """Function to filter a list of plans by currency"""
    return [plan for plan in plans if plan['currency'] == currency]

def reject_free_plans(plans):
    """Function to reject plans with trial period days"""
    return [plan for plan in plans if plan['trial_period_days'] is None]

def filter_free_plans(plans):
    """Function to filter plans with trial period days"""
    return [plan for plan in plans if plan['trial_period_days']]

# Helper functions for Invoice services
invoice_filter_keys = ['total', 'subtotal', 'lines', 'paid', 'period_end', 'period_start',
                       'tax', 'tax_percent', 'currency', 'date', 'id', 'application_fee']

lines_filter_keys = ['plan', 'period', 'currency', 'amount']

def get_invoices_list_response(invoices, email):
    """Function to customize the response of the invoices list

    :param invoices: invoices data from stripe
    :param email: email of the customer to be attach in every invoice
    :return: invoice list as the frontend side is requiring
    """
    invoice_list = []
    for invoice in invoices:
        invoice_dict = filtering_dict_by_keys(invoice.__dict__['_previous'], invoice_filter_keys)
        invoice_dict['email'] = email
        invoice_dict['lines'] = customize_invoice_lines(invoice_dict['lines'])
        invoice_list.append(invoice_dict)
    return invoice_list

def customize_invoice_lines(lines):
    """Function to customize the response of the lines inside an invoice"""
    return [filtering_dict_by_keys(i, lines_filter_keys) for i in lines['data']]

# Helper miscellaneous functions
def get_timestamp_from_datetime(datetime):
    """Function to get a unix timestamp from a datetime object"""
    return int(time.mktime(datetime.timetuple()))

def filtering_dict_by_keys(dic, key_list):
    """Function that returns a filtered dictionary given the keys list"""
    return dict((key, value) for key, value in dic.iteritems() if key in key_list)
