# pip3 install beautifulsoup4 --break-system-packages
from bs4 import BeautifulSoup
# pip3 install lxml --break-system-packages
from lxml import etree
import pprint
import glob
import re

marketplace = "employer" # employer/individual
year = "2025" # 2024

# note: to open all the tabs via javascript you can run:
# $(".comparePlan-tabs").click() to open everything

# TODO: could improve the gathering of the HTML for sure, probably automate it, but the javascript loading of the page makes it hard
# it returns you to the fucking first page every time you click on one, so it makes sense to basically open 41 tabs I guess and click on the right one and then save?
# Update: wrote the scraper, it wasn't horrible but needed to be different depending on whether it was the individual or SHOP marketplace

def getCarrier(html):
	if "emblemhealth.com" in html:
		return "Emblem Health"
	elif "UnitedHealthcare.png" in html:
		return "United Healthcare"
	elif "anthem.com" in html:
		return "Anthem"
	elif "hioscar.com" in html:
		return "Oscar"
	elif "healthfirst.org" in html:
		return "Healthfirst"
	elif "fideliscare.org" in html:
		return "Ambetter from Fidelis Care"
	elif "metroplus.org" in html:
		return "MetroPlusHealth"
	return "Could not determine carrier"

def is_numerical(value):
	
	# remove dollar signs
	value = value.replace("$", "")
	
	# Check if the cleaned string is a valid numeric string
	try:
		float(value)
		return True
	except ValueError:
		return False

def parseIndividualPlan(htmlPath):
	
	html = open(htmlPath).read()
	soup = BeautifulSoup(html, "html.parser")

	# note: for some reason had to remove the tbody's in these for them to work, copied full xpath from Chrome
	root = etree.HTML(html)
	plan = root.xpath('/html/body/div/div[3]/div/div/div/form[1]/table[1]/tr/th[3]')[0].text
	carrier = getCarrier(html)
	link = html.split("Scrapers link to plan:")[1]
	metalLevel = root.xpath('/html/body/div[1]/div[3]/div/div/div/form[1]/table[2]/tr[1]/td[2]/div')[0].text
	premium = root.xpath('/html/body/div[1]/div[3]/div/div/div/form[1]/table[2]/tr[1]/td[1]/div/span')[0].text
	deductible = root.xpath('/html/body/div[1]/div[3]/div/div/div/form[1]/table[2]/tr[3]/td[3]')[0].text.split("/")[0]
	outOfPocketMax = root.xpath('/html/body/div[1]/div[3]/div/div/div/form[1]/table[2]/tr[2]/td[1]')[0].text.split("/")[0]

	# complicated, tables
	try:
		therapyCostRaw = soup.find('div', string=re.compile(r'\s*Mental/Behavioral Health Outpatient Services\s*')).find_parent('td').find_next_sibling('td').text
		specialistCostRaw = soup.find('div', string=re.compile(r'\s*Specialist Visit\s*')).find_parent('td').find_next_sibling('td').text
		primaryCareCostRaw = soup.find('div', string=re.compile(r'\s*Primary Care Visit to Treat an Injury or Illness\s*')).find_parent('td').find_next_sibling('td').text
		bloodDrawRaw = soup.find('div', string=re.compile(r'\s*Laboratory Outpatient and Professional Services\s*')).find_parent('td').find_next_sibling('td').text
		psychiatristCostRaw = therapyCostRaw
		urgentCareRaw = soup.find('div', string=re.compile(r'\s*Urgent Care Centers or Facilities\s*')).find_parent('td').find_next_sibling('td').text
		surgeryFacilityRaw = soup.find('div', string=re.compile(r'\s*Outpatient Facility Fee \(e.g., Ambulatory Surgery Center\)\s*')).find_parent('td').find_next_sibling('td').text
		surgeryServicesRaw = soup.find('div', string=re.compile(r'\s*Outpatient Surgery Physician/Surgical Services\s*')).find_parent('td').find_next_sibling('td').text
		genericDrugsRaw = soup.find('div', string=re.compile(r'\s*Generic Drugs\s*')).find_parent('td').find_next_sibling('td').text
	except:
		print("Unable to parse price data for", plan.strip(), "likely because it's a dental plan, but you should check.")
		print("		", link.strip())
		return None
	
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

# different HTML structure than the individual plans
def parseSHOPPlan(htmlPath):

	html = open(htmlPath).read()
	soup = BeautifulSoup(html, "html.parser")

	root = etree.HTML(html)
	plan = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/div[1]/div/div/h5')[0].text
	carrier = getCarrier(html)
	link = "https://nystateofhealth.ny.gov" + soup.find("form", {"id" : "backToComparePlan"}).get('action')
	# note: for some reason had to remove the tbody's in these for them to work, copied full xpath from Chrome
	metalLevel = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/div[1]/table/tr[1]/td[2]')[0].text
	premium = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/table[1]/tr[1]/td[2]/span')[0].text
	deductible = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/table[1]/tr[3]/td[2]/span')[0].text
	outOfPocketMax = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/table[1]/tr[4]/td[2]/span')[0].text

	# complicated, tables
	target_div = root.xpath('//div[@class="subCol" and text()="Mental/Behavioral Health Outpatient Services"]')[0]
	therapyCostRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

	target_div = root.xpath('//div[@class="subCol" and text()="Specialist Visit"]')[0]
	specialistCostRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

	target_div = root.xpath('//div[@class="subCol" and text()="Primary Care Visit to Treat an Injury or Illness"]')[0]
	primaryCareCostRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

	target_div = root.xpath('//div[@class="subCol" and text()="Laboratory Outpatient and Professional Services"]')[0]
	bloodDrawRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

	# same as therapist
	psychiatristCostRaw = therapyCostRaw

	target_div = root.xpath('//div[@class="subCol" and text()="Urgent Care Centers or Facilities"]')[0]
	urgentCareRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

	target_div = root.xpath('//div[@class="subCol" and text()="Outpatient Facility Fee (e.g., Ambulatory Surgery Center)"]')[0]
	surgeryFacilityRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

	target_div = root.xpath('//div[@class="subCol" and text()="Outpatient Surgery Physician/Surgical Services"]')[0]
	surgeryServicesRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

	target_div = root.xpath('//div[@class="subCol" and text()="Generic Drugs"]')[0]
	genericDrugsRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

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


plans = []
if marketplace == "employer":
	for file in glob.glob(f"plans/automated/employer_{year}*.html"):
		plans.append(parseSHOPPlan(file))
elif marketplace == "individual":
	#for file in glob.glob(f"plans/automated/individual_2025_126895.html"):
	for file in glob.glob(f"plans/automated/individual_{year}*.html"):
		plans.append(parseIndividualPlan(file))


# clean it up a bit
for plan in plans:
	if plan is None: continue # we logged this already, it's probably a dental plan
	for key, value in plan.items():
		plan[key] = value.strip().replace("$", "")

# parse it out a bit
processedPlans = []
for plan in plans:
	if plan is None: continue # we logged this already, it's probably a dental plan
	processedPlan = {}
	for key, value in plan.items():
		# print(key, value)
		if "Raw" not in key:
			# straightforward
			processedPlan[key] = value
		else:
			costName = key.replace("Raw", "")
			# if it's a numberical value, then it's very straightforward 
			if is_numerical(value):
				processedPlan[costName+"BeforeDeductible"] = processedPlan[costName+"AfterDeductible"] = value.strip()
			else:
				# there's some sort of difference or it's weird formatting
				if "Copay after deductible" in value:
					raw = value.replace("Copay after deductible", "")
					processedPlan[costName+"BeforeDeductible"] = "FULL CHARGE"
					processedPlan[costName+"AfterDeductible"] = raw.strip()
				elif "Coinsurance after deductible" in value:
					raw = value.replace("Coinsurance after deductible" , "")
					processed = float(raw.strip().replace("%", "")) / 100
					processedPlan[costName+"BeforeDeductible"] = "FULL CHARGE"
					processedPlan[costName+"AfterDeductible"] = "PARTIAL CHARGE: {}".format(processed)
				elif "No Charge after deductible" in value:
					processedPlan[costName+"BeforeDeductible"] = "FULL CHARGE"
					processedPlan[costName+"AfterDeductible"] = "0"
				elif "No Charge" == value:
					processedPlan[costName+"BeforeDeductible"] = "0"
					processedPlan[costName+"AfterDeductible"] = "0"
				elif "%" in value:
					# it's just flat co-insurance
					processed = float(value.strip().replace("%", "")) / 100
					processedPlan[costName+"BeforeDeductible"] = "PARTIAL CHARGE: {}".format(processed)
					processedPlan[costName+"AfterDeductible"] = "PARTIAL CHARGE: {}".format(processed)

	# pprint.pprint(processedPlan)
	processedPlans.append(processedPlan)

# finally, for the printing:
for plan in processedPlans:

	# for when there's a full charge
	fieldsToColumnsMap = {
		"therapyCost" : "$BN$2",
		"specialistCost" : "$BN$3",
		"primaryCareCost" : "$BN$4",
		"bloodDrawCost" : "$BN$5",
		"psychiatristCost" : "$BN$6",
		"urgentCareCost" : "$BN$7",
		"surgeryFacilitiesCost" : "$BN$8",
		"surgeryServicesCost" : "$BN$9",
		"genericDrugsCost" : "$BN$10"
	}

	if marketplace == "employer":
		finalString = '"SHOP NYS Marketplace", '
	elif marketplace == "individual":
		finalString = '"NYS Individual Marketplace", '

	# to get them to print in a certain order, probably better way to do this
	#pprint.pprint(plan)
	for column in ["carrier", "plan", "link", "level", "premium", "deductible", "outOfPocketMax", "therapyCostBeforeDeductible", "therapyCostAfterDeductible", "specialistCostBeforeDeductible", "specialistCostAfterDeductible", "primaryCareCostBeforeDeductible", "primaryCareCostAfterDeductible", "bloodDrawCostBeforeDeductible", "bloodDrawCostAfterDeductible", "psychiatristCostBeforeDeductible", "psychiatristCostAfterDeductible", "urgentCareCostBeforeDeductible", "urgentCareCostAfterDeductible", "surgeryFacilitiesCostBeforeDeductible", "surgeryFacilitiesCostAfterDeductible", "surgeryServicesCostBeforeDeductible", "surgeryServicesCostAfterDeductible", "genericDrugsCostBeforeDeductible", "genericDrugsCostAfterDeductible"]:
		value = plan[column]

		chosenPair = None
		for key, spreadsheetPair in fieldsToColumnsMap.items():
			if column.startswith(key):
				chosenPair = spreadsheetPair
				break
		#if column == "link":
			# finalString += "=HYPERLINK(\"{}\")".format(value) + ", "
		#	pass
		if value == "FULL CHARGE": 
			finalString += "=" + chosenPair + ", "
		elif "PARTIAL CHARGE: " in value:
			coinsurance = value.replace("PARTIAL CHARGE: ", "")
			finalString += "={}*{}".format(chosenPair, coinsurance) + ", "
		else:
			finalString += '"{}", '.format(value)
	finalString = finalString.rstrip(", ")

	print(finalString)

print("Copy and paste the above, paste it in the spreadsheet, then do a reset on the background color and on the text color, then with everything selected change it to field type money, then reduce the decimal places count.")