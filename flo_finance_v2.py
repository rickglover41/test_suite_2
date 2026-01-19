def flo_finance(staff_rate,agency_rate,rn_need):
	hours_replaced = rn_need*1872*3
	agency_staff_diff = agency_rate-staff_rate
	agency_cost = hours_replaced*agency_staff_diff
	flo_costs = rn_need*50000
	fica_savings = staff_rate*0.0765*hours_replaced
	savings = agency_cost-flo_costs+fica_savings
	return savings

def flo_finance_alt(staff_rate,agency_rate,rn_need):
	hours_replaced = rn_need*1872*3
	new_agency_rate = agency_rate*1.2
	agency_staff_diff = new_agency_rate-staff_rate
	agency_cost = hours_replaced*agency_staff_diff
	flo_costs = rn_need*50000
	fica_savings = staff_rate*0.0765*hours_replaced
	savings = agency_cost-flo_costs+fica_savings
	return savings