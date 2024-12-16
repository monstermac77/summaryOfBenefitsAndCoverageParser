import pprint
import csv

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

