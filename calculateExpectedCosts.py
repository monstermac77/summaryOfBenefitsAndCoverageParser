import pprint
import csv
import sys
import random


# argument related
import argparse

# generate all the arguments
# python3 calculateExpectedCosts.py --therapyVisits 26 even --specialistVisits 6 random --primaryCareVisits 3 even --bloodDrawVisits 2 even --psychiatristVisits 4 even --urgentCareVisits 2 even --surgeries 1 random --prescriptionFills 12 even
parser = argparse.ArgumentParser()
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
	pprint.pprint(plan)
	plan["state"] = {
		# "spentTowardDeductible" : 0,
		# "coinsurancePaid" : 0, # can't distinguish with the data fed in
		# "copaysPaid" : 0, # can't distinguish with the data fed in
		"spentOutOfPocket" : 0
	}
	for day, services in servicesByDay.items():
		for service in services: 	

			# figure out if we should use predeductible, postdeductible,
			# or blend (if this is the service that pushes us over)
			# note: this is technically incorrect, we really need to know whether it's a coinsurence or a copay for these
			# because that'll affect how the calculations work out, but we're going to accept that as a shortcoming for now
			if plan["state"]["spentOutOfPocket"] < plan["deductible"]:
				print("yes below")
				# does this push us over? 
				if plan[service+"CostBeforeDeductible"] + plan["state"]["spentOutOfPocket"] >= plan["deductible"]:
					chargePreDeductible = plan[service+"CostBeforeDeductible"] + plan["state"]["spentOutOfPocket"] - plan["deductible"]
					# for a big charge though, you're not going to be charged the entire amount if it gets you above your deductible
					chargePreDeductible = min(chargePreDeductible, plan["deductible"])
					chargePostDeductible = max(plan[service+"CostAfterDeductible"] - chargePreDeductible, 0) # not sure on this, it could just be the entire cost after deductible but unlikely
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

			print(service, "rendered:", "individual paid", chargePreDeductible, "pre deductible and", chargePostDeductible, "post deductible. Now has spent", plan["state"]["spentOutOfPocket"], "out of pocket.")

	exit()