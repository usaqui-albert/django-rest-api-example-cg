def get_response_plan_list(plans):
    return [{"id": i.id, "name": i.name} for i in plans]
