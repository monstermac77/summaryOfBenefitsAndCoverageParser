# pip3 install "camelot-py[base]"
# pip3 install opencv-python
# pip3 uninstall PyPDF2 
# pip3 install PyPDF2==2.12.1
# pip3 install ghostscript
# brew install ghostscript
# still didn't work, and messed up paths stuff so undid
# import camelot
# tables = camelot.read_pdf("summaryOfBenefitsAndCoveragePDFs/2024-2025-aetna-justworks-medical-c3-sbc.pdf")
# tables.export('foo.csv', f='csv', compress=False)

# pip install tika
# then got RuntimeError: Unable to start Tika server
# installed brew
# nano ~/.zshrc and add export PATH=$PATH:/opt/homebrew/bin
# sudo softwareupdate --install-rosetta
# brew tap adoptopenjdk/openjdk
# brew install --cask adoptopenjdk8
from tika import parser 
import re
import glob
import pprint
from shared import getCarrier
from shared import cleanPlan
from shared import processPlan
from shared import printPlan
from shared import getPremiumForPlan

def replace_multiple_spaces(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()

def getNumberFromString(string):
	# TODO: should figure these out, probably upstream issue
	try:
		string = string.replace(",", "")
		find = re.findall(r'\d+', string)[0]
	except:
		find = "9999"
	return find

def getMetalLevel(string):
	if "platinum" in string.lower():
		return "Platinum"
	elif "gold" in string.lower():
		return "Gold"
	elif "silver" in string.lower():
		return "Silver"
	elif "bronze" in string.lower():
		return "Bronze"
	elif "catastrophic" in string.lower():
		return "Catastrophic"

def parsePlan(rawStripped):
	string = rawStripped.split("Summary of Benefits and Coverage: What this Plan Covers & What You Pay for Covered Services")[1].split("The Summary of Benefits and Coverage (SBC) document")[0]
	if "Managed Choice®" in string:
		string = string.split("Managed Choice®")[1]
	string = string.strip().strip("-").strip()
	return string


def extractSBCData(path):
	raw = parser.from_file(path)['content']
	rawStripped = replace_multiple_spaces(raw.replace("\n", " "))

	# carrier
	carrier = getCarrier(rawStripped)

	# plan
	plan = parsePlan(rawStripped)

	# link
	# TODO: this would need to change if more were added
	link = "https://secure.justworks.com/insurance_policy_document/summaries-of-benefits-coverage/" + path.split("/")[-1]

	# level
	metalLevel = getMetalLevel(rawStripped)

	# premium
	# unfortunately this can't be gathered from the PDF, it's not on there, will have to be added manually
	# TODO: this would need to change if more were added
	premium = getPremiumForPlan(path.split("/")[-1])

	# deductible
	section = rawStripped.split("What is the overall deductible?")[1].split("Are there services covered before")[0]
	reduced = section.split(" Out")[0]
	if ":" in reduced:
		reduced = reduced.split(":")[1]
	if "/" in reduced:
		reduced = reduced.split("/")[0]
	deductible = getNumberFromString(reduced)

	# out of pocket max
	section = rawStripped.split("What is the out-of-pocket limit for this plan?")[1].split("The out-of-pocket limit is the most you could")[0]
	reduced = section.split(" Out")[0]
	if ":" in reduced:
		reduced = reduced.split(":")[1]
	if "/" in reduced:
		reduced = reduced.split("/")[0]
	outOfPocketMax = getNumberFromString(reduced)

	# note: need to handle deductible does not apply for these 
	defaultIsPostDeductible = ("All copayment and coinsurance costs shown in this chart are after your deductible has been met, if a deductible applies." in rawStripped)
	
	# therapy 
	section = rawStripped.split("If you need mental health, behavioral health, or substance abuse services")[1].replace(" Outpatient services Office: ", "").strip()
	smallLookahead = section[:100]
		
	if " " in section:
		section = section.split(" ")[0]
	if section == "Outpatient":
		section = rawStripped.split("If you need mental health, behavioral health, or substance abuse services")[1].split("Outpatient services Office & other outpatient services:")[1].strip()
		if " " in section:
			section = section.split(" ")[0]
	therapyCostRaw = section.replace("Outpatient services Office:", "").strip()
	if "$" not in therapyCostRaw and "%" not in therapyCostRaw:
		therapyCostRaw = "Unknown"

	if "deductible doesn't apply" not in smallLookahead:
		therapyCostRaw = therapyCostRaw + (" Coinsurance" if "%" in therapyCostRaw else " Copay") + " after deductible"
	
	# specialist 
	section = rawStripped.split("Specialist visit ")[1].split("Office & other outpatient")[0]
	smallLookahead = section[:70]
	section = section.split("copay/visit")[0].split("copay per visit")[0]
	if " " in section:
		section = section.split(" ")[0]
	specialistCostRaw = section

	if "deductible doesn't apply" not in smallLookahead:
		specialistCostRaw = specialistCostRaw + (" Coinsurance" if "%" in specialistCostRaw else " Copay") + " after deductible"
	
	# primary care
	section = rawStripped.split("Primary care visit to treat an injury or illness")[1].split("Virtual Primary Care telemedicine provider")[0]
	smallLookahead = section[:70]
	section = section.split("copay/visit")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	primaryCareCostRaw = section
	
	if "deductible doesn't apply" not in smallLookahead:
		primaryCareCostRaw = primaryCareCostRaw + (" Coinsurance" if "%" in primaryCareCostRaw else " Copay") + " after deductible"
	
	print(path, primaryCareCostRaw)

	# blood draw
	section = rawStripped.split("Diagnostic test (x-ray, blood work)")[1].split("Imaging ")[0].strip()
	if "No charge for laboratory" in section:
		section = "$0"
	elif " " in section:
		section = section.split(" ")[0]
	bloodDrawRaw = section.split(" coinsurance ")[0]

	# psychiatrist
	psychiatristCostRaw = therapyCostRaw

	# urgent care
	section = rawStripped.split("Urgent care")[1].split("copay/visit")[0].split("copay per visit")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	urgentCareRaw = getNumberFromString(section)

	# surgery facilities
	section = rawStripped.split("Facility fee (e.g., ambulatory surgery center)")[1].split("copay/visit")[0].split(" coinsurance")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	if "%" in section:
		surgeryFacilityRaw = getNumberFromString(section) + "%"
	else:
		surgeryFacilityRaw = getNumberFromString(section)

	# surgery services
	section = rawStripped.split("Physician/surgeon fees")[1].split("copay/visit")[0].split(" coinsurance")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	if "%" in section:
		surgeryServicesRaw = getNumberFromString(section) + "%"
	else:
		surgeryServicesRaw = getNumberFromString(section)

	# generic drugs
	for keyword in ["Preferred generic drugs", "Generic drugs"]:
		if keyword in rawStripped:
			section = rawStripped.split(keyword)[1].split("(retail)")[0]
	genericDrugsRaw = getNumberFromString(section)

	return {
		"carrier" : carrier,
		"plan" : plan,
		"link" : link,
		"level" : metalLevel,
		"premium" : premium,
		"deductible" : deductible,
		"outOfPocketMax"  : outOfPocketMax,
		"therapyCostRaw" : therapyCostRaw,
		"specialistCostRaw" : specialistCostRaw,
		"primaryCareCostRaw" : primaryCareCostRaw,
		"bloodDrawCostRaw" : bloodDrawRaw,
		"psychiatristCostRaw" : psychiatristCostRaw,
		"urgentCareCostRaw" : urgentCareRaw,
		"surgeryFacilitiesCostRaw" : surgeryFacilityRaw,
		"surgeryServicesCostRaw" : surgeryServicesRaw,
		"genericDrugsCostRaw" : genericDrugsRaw
	}

for file in glob.glob(f"summaryOfBenefitsAndCoveragePDFs/*.pdf"):
	# print("Parsing {}...".format(file.split("/")[1]))
	plan = extractSBCData(file)
	#pprint.pprint(plan)
	#pprint.pprint(plan)
	#continue
	plan = cleanPlan(plan, "sbcPDF")
	plan = processPlan(plan, "sbcPDF")
	#printPlan(plan, "sbcPDF")

print("Copy and paste the above, paste it in the spreadsheet, then do a reset on the background color and on the text color, then with everything selected change it to field type money, then reduce the decimal places count.")