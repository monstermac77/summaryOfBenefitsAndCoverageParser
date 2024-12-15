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

def replace_multiple_spaces(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()

def getNumberFromString(string):
     string = string.replace(",", "")
     return re.findall(r'\d+', string)[0]

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

def extractSBCData(path):
	raw = parser.from_file(path)['content']
	rawStripped = replace_multiple_spaces(raw.replace("\n", " "))

	# carrier
	carrier = getCarrier(rawStripped)

	# plan
	plan = rawStripped.split("Summary of Benefits and Coverage: What this Plan Covers & What You Pay for Covered Services")[1].split("The Summary of Benefits and Coverage (SBC) document")[0]

	# level
	metalLevel = getMetalLevel(rawStripped)

	# premium
	# unfortunately this can't be gathered from the PDF, it's not on there, will have to be added manually
	premium = None

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

	# therapy 
	section = rawStripped.split("If you need mental health, behavioral health, or substance abuse services")[1].split("Office & other outpatient")[0].split("other outpatient services")[0]
	therapyCostRaw = getNumberFromString(section.replace("Outpatient services Office:", "").strip())

	# specialist 
	section = rawStripped.split("Specialist visit ")[1].split("Office & other outpatient")[0].split("copay/visit")[0].split("copay per visit")[0]
	specialistCostRaw = getNumberFromString(section)

	# primary care
	section = rawStripped.split("Primary care visit to treat an injury or illness")[1].split("Virtual Primary Care telemedicine provider")[0].split("copay/visit")[0]
	primaryCareCostRaw = getNumberFromString(section)

	# blood draw
	section = rawStripped.split("Diagnostic test (x-ray, blood work)")[1].split("Imaging ")[0]
	bloodDrawRaw = section.split(" coinsurance ")[0] + " coinsurance"

	# psychiatrist
	psychiatristCostRaw = therapyCostRaw

	# urgent care
	section = rawStripped.split("Urgent care")[1].split("copay/visit")[0].split("copay per visit")[0]
	urgentCareRaw = getNumberFromString(section)

	# surgery facilities
	section = rawStripped.split("Facility fee (e.g., ambulatory surgery center)")[1].split("copay/visit")[0].split(" coinsurance")[0]
	if "%" in section:
		surgeryFacilityRaw = getNumberFromString(section) + "% coinsurance"
	else:
		surgeryFacilityRaw = getNumberFromString(section)

	# surgery services
	section = rawStripped.split("Physician/surgeon fees")[1].split("copay/visit")[0].split(" coinsurance")[0]
	if "%" in section:
		surgeryServicesRaw = getNumberFromString(section) + "% coinsurance"
	else:
		surgeryServicesRaw = getNumberFromString(section)

	# generic drugs
	

	return {
		"carrier" : carrier,
		"plan" : plan,
		"link" : None,
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
		# "genericDrugsCostRaw" : genericDrugsRaw
	}

plans = []
for file in glob.glob(f"summaryOfBenefitsAndCoveragePDFs/*.pdf"):
	print("Parsing {}...".format(file.split("/")[1]))
	plan = extractSBCData(file)
	pprint.pprint(plan)
	plans.append(plan)