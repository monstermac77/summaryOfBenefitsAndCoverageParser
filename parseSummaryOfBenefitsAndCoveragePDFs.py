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
from shared import conditionallyApplyDeductibleLanguage

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
	therapyCostRaw = conditionallyApplyDeductibleLanguage(therapyCostRaw, smallLookahead)
	
	# specialist 
	section = rawStripped.split("Specialist visit ")[1].split("Office & other outpatient")[0]
	smallLookahead = section[:70]
	section = section.split("copay/visit")[0].split("copay per visit")[0]
	if " " in section:
		section = section.split(" ")[0]
	specialistCostRaw = conditionallyApplyDeductibleLanguage(section, smallLookahead)

	# primary care
	section = rawStripped.split("Primary care visit to treat an injury or illness")[1].split("Virtual Primary Care telemedicine provider")[0]
	smallLookahead = section[:70]
	section = section.split("copay/visit")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	primaryCareCostRaw = conditionallyApplyDeductibleLanguage(section, smallLookahead)
	
	# blood draw
	section = rawStripped.split("Diagnostic test (x-ray, blood work)")[1].split("Imaging ")[0].strip()
	smallLookahead = section[:70]
	if "No charge for laboratory" in section:
		bloodDrawRaw = "$0"
	else:
		if " " in section:
			section = section.split(" ")[0]
		bloodDrawRaw = section.split(" coinsurance ")[0]
		bloodDrawRaw = conditionallyApplyDeductibleLanguage(bloodDrawRaw, smallLookahead)
	
	# psychiatrist
	psychiatristCostRaw = therapyCostRaw

	# urgent care
	section = rawStripped.split("Urgent care")[1]
	smallLookahead = section[:70]
	section = section.split("copay/visit")[0].split("copay per visit")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	urgentCareRaw = conditionallyApplyDeductibleLanguage(section, smallLookahead)

	# surgery facilities
	section = rawStripped.split("Facility fee (e.g., ambulatory surgery center)")[1]
	smallLookahead = section[:70]
	section = section.split("copay/visit")[0].split(" coinsurance")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	surgeryFacilityRaw = conditionallyApplyDeductibleLanguage(section, smallLookahead)

	# surgery services
	section = rawStripped.split("Physician/surgeon fees")[1]
	smallLookahead = section[:70]
	section = section.split("copay/visit")[0].split(" coinsurance")[0].strip()
	if " " in section:
		section = section.split(" ")[0]
	surgeryServicesRaw = conditionallyApplyDeductibleLanguage(section, smallLookahead)

	# generic drugs
	for keyword in ["Preferred generic drugs", "Generic drugs"]:
		if keyword in rawStripped:
			section = rawStripped.split(keyword)[1]
			smallLookahead = section[:70]
			section = section.split("(retail)")[0].replace("Copay/prescription", "").split(" coinsurance")[0].split("Copay")[0]
	genericDrugsRaw = conditionallyApplyDeductibleLanguage(section, smallLookahead)
	addition = ""
	if "%" in genericDrugsRaw:
		addition = "%"
	genericDrugsRaw = getNumberFromString(genericDrugsRaw) + addition

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

for folder in ["public", "confidential"]:
	for file in glob.glob(f"summaryOfBenefitsAndCoveragePDFs/{folder}/*.pdf"):
		# print("Parsing {}...".format(file.split("/")[1]))
		plan = extractSBCData(file)
		#pprint.pprint(plan)
		#pprint.pprint(plan)
		#continue
		plan = cleanPlan(plan, "sbcPDF")
		plan = processPlan(plan, "sbcPDF")
		printPlan(plan, "sbcPDF")

print("Duplicate the Health Insurance Options spreadsheet from last year. Copy the above. Save the above as a CSV on your desktop. Delete the existing data from the google sheet copy, keep the headers. Select row 2. Do an import on Google sheets and select Append to current sheet. then do a reset on the background color and on the text color (if needed), then with everything selected change it to field type money, then reduce the decimal places count. Then go to column BL in the new sheet and copy all of the variables from the old sheet from BL into the new sheet so that these are defined and all of the values can be calculated.")
print("Once you have all of these worked out, you can skip to the calculateExpectedCosts because you have all the raw data you need in the sheet. If you want to get the Master sheet all nice like we had it in 2025, go ahead, but the calculate expected costs is sufficient we believe.")
print("To do this, copy everything in the Master sheet up to generic drug cost after deductible, and then paste it in the master for export sheet but paste values only, so that it's just raw values no formulas.")
print("Rename the old processedData.csv file as processedData[year].csv, and then download the new data you just made as processedData.csv and put it in the folder.")
print("Be sure to delete everything after the generic drug cost after deductible header, inlcuding the headers and any empty columns for all the rows, there are likely some depending on how you did the export, we only want filled in rows and non blank columns.")