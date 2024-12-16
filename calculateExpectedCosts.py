import pprint
import csv
import sys

# argument related
import argparse

# generate all the arguments
# python3 calculateExpectedCosts.py --therapyVisits 26 event --specialistVisits 6 random --primaryCareVisits 3 even --bloodDrawVisits 2 even --psychiatristVisits 4 even --urgentCareVisits 2 even --surgeries 1 random --prescriptionFills 12 even
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
	14 : "bloodsDrawsCostBeforeDeductible",
	15 : "bloodsDrawsCostAfterDeductible",
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
			plan[columnMap[index]] = datum
		plans.append(plan)

