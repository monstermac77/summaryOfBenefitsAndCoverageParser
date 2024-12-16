import pprint
import csv
import sys

# argument related
import argparse

# generate all the arguments
# python3 calculateExpectedCosts.py --therapyVisits 26 --specialistVisits 6 --primaryCareVisits 3 --bloodDrawVisits 2 --psychiatristVisits 4 --urgentCareVisits 2 --surgeries 1 --prescriptionFills 12
parser = argparse.ArgumentParser()
parser.add_argument("--therapyVisits", help="the number of therapy sessions you expect to have in a given year", metavar='therapies')
parser.add_argument("--specialistVisits", help="the number of specialist visits you expect to have in a given year", metavar='specialists')
parser.add_argument("--primaryCareVisits", help="the number of primary care visits you expect to have in a given year", metavar='primaries')
parser.add_argument("--bloodDrawVisits", help="the number of blood draws you expect to have in a given year", metavar='bloods')
parser.add_argument("--psychiatristVisits", help="the number of psychiatrist visits you expect to have in a given year", metavar='psychiatrists')
parser.add_argument("--urgentCareVisits", help="the number of urgent care visits you expect to have in a given year", metavar='urgentCares')
parser.add_argument("--surgeries", help="the number of surgeries you expect to have in a given year", metavar='surgeries')
parser.add_argument("--prescriptionFills", help="the number of prescription fills you expect to have in a given year", metavar='prescriptions')

# if the developer didn't specify what to run, give them some help
if len(sys.argv) == 1:
	parser.print_help(sys.stderr)
	sys.exit(1)

# actually parse out the args
args = parser.parse_args()

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
	8 : "therapyCostBeforeDeductible",
	9 : "therapyCostAfterDeductible",
	10 : "specialistCostBeforeDeductible",
	11 : "specialistCostAfterDeductible",
	12 : "primaryCareCostBeforeDeductible",
	13 : "primaryCareCostAfterDeductible",
	14 : "bloodDrawCostBeforeDeductible",
	15 : "bloodDrawCostAfterDeductible",
	16 : "psychiatristCostBeforeDeductible",
	17 : "psychiatristCostAfterDeductible",
	18 : "urgentCareCostBeforeDeductible",
	19 : "urgentCareCostAfterDeductible",
	20 : "surgeryFacilityCostBeforeDeductible",
	21 : "surgeryFacilityCostAfterDeductible",
	22 : "surgeryServicesCostBeforeDeductible",
	23 : "surgeryServicesCostAfterDeductible",
	24 : "genericDrugCostBeforeDeductible",
	25 : "genericDrugCostAfterDeductible"
}

# we could ingest the processed data, which we probably want to do eventually, but a CSV intermediary is nice so that 
# any data can be checked / corrected if needed

plans = []
with open('processedData.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',', quotechar='"')
	for row in reader:
		plan = {}
		for index, datum in enumerate(row):
			plan[columnMap[index]] = datum
		plans.append(plan)

