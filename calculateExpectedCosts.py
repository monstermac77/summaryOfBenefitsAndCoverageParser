import pprint
import csv
import sys
import random


# argument related
import argparse

# generate all the arguments
# python3 calculateExpectedCosts.py --therapyVisits 26 even --specialistVisits 6 random --primaryCareVisits 3 even --bloodDrawVisits 2 even --psychiatristVisits 4 even --urgentCareVisits 2 even --surgeries 1 random --prescriptionFills 12 even
parser = argparse.ArgumentParser()
parser.add_argument("simulations", help="the number of times you want to simulate the plans, the more simulations the more accurate the estimate", metavar='simulations')
parser.add_argument("costShare", help="the percent that you want the employee to pay", metavar='costShare')
parser.add_argument("--therapyVisits", help="the number of therapy sessions you expect to have in a given year", nargs=2, metavar=('therapies','therapiesDistro'))
parser.add_argument("--specialistVisits", help="the number of specialist visits you expect to have in a given year", nargs=2, metavar=('specialists','specialistsDistro'))
parser.add_argument("--primaryCareVisits", help="the number of primary care visits you expect to have in a given year", nargs=2, metavar=('primaries','primariesDistro'))
parser.add_argument("--bloodDrawVisits", help="the number of blood draws you expect to have in a given year", nargs=2, metavar=('bloodDraws','bloodDrawsDistro'))
parser.add_argument("--psychiatristVisits", help="the number of psychiatrist visits you expect to have in a given year", nargs=2, metavar=('psychiatrists','psychiatristsDistro'))
parser.add_argument("--urgentCareVisits", help="the number of urgent care visits you expect to have in a given year", nargs=2, metavar=('urgentCares','urgentCaresDistro'))
parser.add_argument("--surgeries", help="the number of surgeries you expect to have in a given year", nargs=2, metavar=('surgeries','surgeriesDistro'))
parser.add_argument("--prescriptionFills", help="the number of prescription fills you expect to have in a given year", nargs=2, metavar=('prescriptions','prescriptionsDistro'))

# should output: 
# best sequence with cost
# worst sequence with cost
# average cost

# if the developer didn't specify what to run, give them some help
if len(sys.argv) == 1:
	parser.print_help(sys.stderr)
	sys.exit(1)

def roundedAverage(numbers):
	return int(sum(numbers)/len(numbers))

# actually parse out the args
args = parser.parse_args()
therapies, therapiesDistro = int(args.therapyVisits[0]), args.therapyVisits[0]
specialists, specialistsDistro = int(args.specialistVisits[0]), args.specialistVisits
primaries, primariesDistro = int(args.primaryCareVisits[0]), args.primaryCareVisits
bloodDraws, bloodDrawsDistro = int(args.bloodDrawVisits[0]), args.bloodDrawVisits
psychiatrists, psychiatristsDistro = int(args.psychiatristVisits[0]), args.psychiatristVisits
urgentCares, urgentCaresDistro = int(args.urgentCareVisits[0]), args.urgentCareVisits
surgeries, surgeriesDistro = int(args.surgeries[0]), args.surgeries
prescriptions, prescriptionsDistro = int(args.prescriptionFills[0]), args.prescriptionFills

# note: we kind of want to keep the ratio relative to the expected cost of the services for coinsurance so that 
# you can freely change those variables and recalculate without updating the spreadsheet
columnMap = {
	0 : "source",
	1 : "company",
	2 : "plan",
	3 : "link", 
	4 : "level", 
	5 : "premium", 
	6 : "deductible", 
	7 : "outOfPocketMax", 
	8 : "therapiesCostBeforeDeductible",
	9 : "therapiesCostAfterDeductible",
	10 : "specialistsCostBeforeDeductible",
	11 : "specialistsCostAfterDeductible",
	12 : "primariesCostBeforeDeductible",
	13 : "primariesCostAfterDeductible",
	14 : "bloodDrawsCostBeforeDeductible",
	15 : "bloodDrawsCostAfterDeductible",
	16 : "psychiatristsCostBeforeDeductible",
	17 : "psychiatristsCostAfterDeductible",
	18 : "urgentCaresCostBeforeDeductible",
	19 : "urgentCaresCostAfterDeductible",
	20 : "surgeryFacilityCostBeforeDeductible",
	21 : "surgeryFacilityCostAfterDeductible",
	22 : "surgeryServicesCostBeforeDeductible",
	23 : "surgeryServicesCostAfterDeductible",
	24 : "prescriptionsCostBeforeDeductible",
	25 : "prescriptionsCostAfterDeductible"
}

# we could ingest the processed data, which we probably want to do eventually, but a CSV intermediary is nice so that 
# any data can be checked / corrected if needed

plans = []
with open('processedData.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		plan = {}
		for index, datum in enumerate(row):
			plan[columnMap[index]] = int(datum.replace("$", "").replace(",", "")) if "$" in datum  else datum
		plans.append(plan)

# now we want to find the interval for each of the services for the individual
intervalByService = {
	"therapies" : round(365 / therapies),
	"specialists" : round(365 / specialists),
	"primaries" : round(365 / primaries),
	"bloodDraws" : round(365 / bloodDraws),
	"psychiatrists" : round(365 / psychiatrists),
	"urgentCares" : round(365 / urgentCares),
	"surgeries" : round(365 / surgeries),
	"prescriptions" : round(365 / prescriptions),
}

totalsAcrossSimulations = {
}

def simulate():

	startingDayByService = {
		service : random.randint(1, interval) for service, interval in intervalByService.items()
	}

	servicesByDay = {
		index : [] for index in range(1, 366)
	}

	# now fill in the services by day
	for service, startingDay in startingDayByService.items():
		currentDay = startingDay
		while currentDay <= 365:
			# certain things are kind of grouped, like surgeries
			if service == "surgeries":
				servicesByDay[currentDay].extend(["surgeryFacility", "surgeryServices"])
			else:	
				servicesByDay[currentDay].append(service)
			currentDay += intervalByService[service]


	# now for each plan, go day by day
	for plan in plans: 

		# let's ignore everything except Aetna for now
		if plan["company"] != "Aetna": continue

		plan["state"] = {
			# "spentTowardDeductible" : 0,
			# "coinsurancePaid" : 0, # can't distinguish with the data fed in
			# "copaysPaid" : 0, # can't distinguish with the data fed in
			"spentOutOfPocket" : 0
		}
		justHitDeductible = False
		for day, services in servicesByDay.items():
			for service in services: 	

				# figure out if we should use predeductible, postdeductible,
				# or blend (if this is the service that pushes us over)
				# note: this is technically incorrect, we really need to know whether it's a coinsurence or a copay for these
				# because that'll affect how the calculations work out, but we're going to accept that as a shortcoming for now
				if plan["state"]["spentOutOfPocket"] < plan["deductible"]:
					# does this push us over? 
					if plan[service+"CostBeforeDeductible"] + plan["state"]["spentOutOfPocket"] > plan["deductible"]:
						chargePreDeductible = abs(plan["state"]["spentOutOfPocket"] - plan["deductible"])
						# for a big charge though, you're not going to be charged the entire amount if it gets you above your deductible
						if chargePreDeductible > plan["deductible"]:
							chargePreDeductible = min(chargePreDeductible, plan["deductible"])
						chargePostDeductible = max(plan[service+"CostAfterDeductible"] - chargePreDeductible, 0) # not sure on this, it could just be the entire cost after deductible but unlikely
						justHitDeductible = True
					else:
						# if it doesn't, it's simple
						chargePreDeductible = plan[service+"CostBeforeDeductible"]
						chargePostDeductible = 0
				else:
					# we already met the deductible
					chargePreDeductible = 0
					chargePostDeductible = plan[service+"CostAfterDeductible"]
				
				# now we know the total charge for the service
				plan["state"]["spentOutOfPocket"] += (chargePreDeductible + chargePostDeductible)
				extraPrint = ""
				if justHitDeductible:
					extraPrint = "DEDUCTIBLE HIT"
					justHitDeductible = False
				# print(f"On day {day}", service, "rendered:", "individual paid", chargePreDeductible, "pre deductible and", chargePostDeductible, "post deductible. Now has spent", plan["state"]["spentOutOfPocket"], f"out of pocket. {extraPrint}")

		key = plan['company'] + " " + plan['plan']
		if key not in totalsAcrossSimulations: totalsAcrossSimulations[key] = {
			"totalPremiums" : [],
			"employeePremiumTotal" : [],
			"employeeCopayTotal" : [],
			"coursicleCostTotal" : [],
			"employeeCostTotal" : [],
			"totalCost" : [],
			"totalCostTaxAdjusted" : [],
			"plan" : plan
		}
			
		yearlyPremium = plan["premium"] * 12

		totalsAcrossSimulations[key]["totalPremiums"].append(
			yearlyPremium
		)

		totalsAcrossSimulations[key]["employeePremiumTotal"].append(
			int(yearlyPremium * (int(args.costShare) / 100))
		)

		totalsAcrossSimulations[key]["employeeCopayTotal"].append(
			plan["state"]["spentOutOfPocket"]
		)

		totalsAcrossSimulations[key]["coursicleCostTotal"].append(
			int(yearlyPremium * (100 - int(args.costShare)) / 100)
		)

		totalsAcrossSimulations[key]["employeeCostTotal"].append(
			int(yearlyPremium * (int(args.costShare) / 100)) + plan["state"]["spentOutOfPocket"]
		)

		totalsAcrossSimulations[key]["totalCost"].append(
			yearlyPremium + plan["state"]["spentOutOfPocket"]
		)

		totalsAcrossSimulations[key]["totalCostTaxAdjusted"].append(
			int(yearlyPremium + 1/(1-0.24) * plan["state"]["spentOutOfPocket"])
		)		


	


for i in range(0, int(args.simulations)):
	simulate()

# calculate averages
for key in totalsAcrossSimulations:
	totals = totalsAcrossSimulations[key]
	totalsAcrossSimulations[key]["averageTaxAdjustedCost"] = roundedAverage(totals["totalCostTaxAdjusted"])
	totalsAcrossSimulations[key]["averageCoursicleCostTotal"] = roundedAverage(totals["coursicleCostTotal"])
	totalsAcrossSimulations[key]["averageEmployeeCostTotal"] = roundedAverage(totals["employeeCostTotal"])
	totalsAcrossSimulations[key]["averageEmployeePremiumTotal"] = roundedAverage(totals["employeePremiumTotal"])
	totalsAcrossSimulations[key]["averageEmployeeCopayTotal"] = roundedAverage(totals["employeeCopayTotal"])

# sort them 
sortedPlans = dict(sorted(totalsAcrossSimulations.items(), key=lambda item: item[1]['averageTaxAdjustedCost']))
print("Plans by cheapest for employee + Coursicle (balanced):")
for planKey in sortedPlans:
	print("	${}".format(totalsAcrossSimulations[planKey]["averageTaxAdjustedCost"]), planKey)
	print("		Premium:", "${}/month".format(totalsAcrossSimulations[planKey]["plan"]["premium"]))
	print("		Deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["deductible"]))
	print("		Out of pocket max:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["outOfPocketMax"]))
	print("		Employee cost (premium):", "${}/month".format(int(totalsAcrossSimulations[planKey]["averageEmployeePremiumTotal"] / 12)))
	print("		Estimated copays/coinsurance:", "${}/month".format(int(totalsAcrossSimulations[planKey]["averageEmployeeCopayTotal"] / 12)))
	print("			Therapy after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["therapiesCostAfterDeductible"]))
	print("			Specialist after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["specialistsCostAfterDeductible"]))
	print("			Primary care after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["primariesCostAfterDeductible"]))
	print("			Blood draws after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["bloodDrawsCostAfterDeductible"]))
	print("			Psychiatrist after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["psychiatristsCostAfterDeductible"]))
	print("			Urgent care after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["urgentCaresCostAfterDeductible"]))
	print("			Surgery facility after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["surgeryFacilityCostAfterDeductible"]))
	print("			Surgery services after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["surgeryServicesCostAfterDeductible"]))

sortedPlans = dict(sorted(totalsAcrossSimulations.items(), key=lambda item: item[1]['averageEmployeeCostTotal']))
print("Plans by cheapest for employee:")
for planKey in sortedPlans:
	print("	${}".format(totalsAcrossSimulations[planKey]["averageEmployeeCostTotal"]), planKey)
	print("		Premium:", "${}/month".format(totalsAcrossSimulations[planKey]["plan"]["premium"]))
	print("		Deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["deductible"]))
	print("		Out of pocket max:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["outOfPocketMax"]))
	print("		Employee cost (premium):", "${}/month".format(int(totalsAcrossSimulations[planKey]["averageEmployeePremiumTotal"] / 12)))
	print("		Estimated copays/coinsurance:", "${}/month".format(int(totalsAcrossSimulations[planKey]["averageEmployeeCopayTotal"] / 12)))
	print("			Therapy after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["therapiesCostAfterDeductible"]))
	print("			Specialist after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["specialistsCostAfterDeductible"]))
	print("			Primary care after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["primariesCostAfterDeductible"]))
	print("			Blood draws after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["bloodDrawsCostAfterDeductible"]))
	print("			Psychiatrist after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["psychiatristsCostAfterDeductible"]))
	print("			Urgent care after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["urgentCaresCostAfterDeductible"]))
	print("			Surgery facility after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["surgeryFacilityCostAfterDeductible"]))
	print("			Surgery services after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["surgeryServicesCostAfterDeductible"]))

sortedPlans = dict(sorted(totalsAcrossSimulations.items(), key=lambda item: item[1]['averageCoursicleCostTotal']))
print("Plans by cheapest for Coursicle:")
for planKey in sortedPlans:
	print("	${}".format(totalsAcrossSimulations[planKey]["averageCoursicleCostTotal"]), planKey)
	print("		Premium:", "${}/month".format(totalsAcrossSimulations[planKey]["plan"]["premium"]))
	print("		Deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["deductible"]))
	print("		Out of pocket max:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["outOfPocketMax"]))
	print("		Employee cost (premium):", "${}/month".format(int(totalsAcrossSimulations[planKey]["averageEmployeePremiumTotal"] / 12)))
	print("		Estimated copays/coinsurance:", "${}/month".format(int(totalsAcrossSimulations[planKey]["averageEmployeeCopayTotal"] / 12)))
	print("			Therapy after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["therapiesCostAfterDeductible"]))
	print("			Specialist after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["specialistsCostAfterDeductible"]))
	print("			Primary care after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["primariesCostAfterDeductible"]))
	print("			Blood draws after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["bloodDrawsCostAfterDeductible"]))
	print("			Psychiatrist after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["psychiatristsCostAfterDeductible"]))
	print("			Urgent care after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["urgentCaresCostAfterDeductible"]))
	print("			Surgery facility after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["surgeryFacilityCostAfterDeductible"]))
	print("			Surgery services after deductible:", "${}".format(totalsAcrossSimulations[planKey]["plan"]["surgeryServicesCostAfterDeductible"]))
