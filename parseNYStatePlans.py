# pip3 install beautifulsoup4 --break-system-packages
from bs4 import BeautifulSoup
# pip3 install lxml --break-system-packages
from lxml import etree
import pprint
import glob
import re

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

	target_div = root.xpath('//div[@class="subCol" and text()="Outpatient Surgery Physician/Surgical Services"]')[0]
	surgeryRaw = target_div.xpath('following::div[@class="subCol"][1]')[0].text

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
		"surgeryCostRaw" : surgeryRaw
	}


plans = []
for file in glob.glob("plans/automated/employer*.html"):
	plans.append(parseSHOPPlan(file))


# clean it up a bit
for plan in plans:
	for key, value in plan.items():
		plan[key] = value.strip().replace("$", "")

# parse it out a bit
processedPlans = []
for plan in plans:
	processedPlan = {}
	for key, value in plan.items():
		if "Raw" not in key:
			# straightforward
			processedPlan[key] = value
		else:
			costName = key.replace("Raw", "")
			# if it's a numberical value, then it's very straightforward 
			if is_numerical(value):
				processedPlan[costName+"BeforeDeductible"] = processedPlan[costName+"AfterDeductible"] = value.strip()
			else:
				# there's some sort of difference
				if "Copay after deductible" in value:
					raw = value.replace("Copay after deductible", "")
					processedPlan[costName+"BeforeDeductible"] = "FULL CHARGE"
					processedPlan[costName+"AfterDeductible"] = raw.strip()
				if "Coinsurance after deductible" in value:
					raw = value.replace("Coinsurance after deductible" , "")
					processed = float(raw.strip().replace("%", "")) / 100
					processedPlan[costName+"BeforeDeductible"] = "FULL CHARGE"
					processedPlan[costName+"AfterDeductible"] = "PARTIAL CHARGE: {}".format(processed)
				if "No Charge after deductible" in value:
					processedPlan[costName+"BeforeDeductible"] = "FULL CHARGE"
					processedPlan[costName+"AfterDeductible"] = "0"
				if "No Charge" == value:
					processedPlan[costName+"BeforeDeductible"] = "0"
					processedPlan[costName+"AfterDeductible"] = "0"

	# pprint.pprint(processedPlan)
	processedPlans.append(processedPlan)

# finally, for the printing:
for plan in processedPlans:

	# for when there's a full charge
	fieldsToColumnsMap = {
		"therapyCost" : "$C$2",
		"specialistCost" : "$C$3",
		"primaryCareCost" : "$C$4",
		"bloodDrawCost" : "$C$5",
		"psychiatristCost" : "$C$6",
		"urgentCareCost" : "$C$7",
		"surgeryCost" : "$C$8"
	}

	finalString = '"SHOP NYS Marketplace", '
	# to get them to print in a certain order, probably better way to do this
	for column in ["carrier", "plan", "link", "level", "premium", "deductible", "outOfPocketMax", "therapyCostBeforeDeductible", "therapyCostAfterDeductible", "specialistCostBeforeDeductible", "specialistCostAfterDeductible", "primaryCareCostBeforeDeductible", "primaryCareCostAfterDeductible", "bloodDrawCostBeforeDeductible", "bloodDrawCostAfterDeductible", "psychiatristCostBeforeDeductible", "psychiatristCostAfterDeductible", "urgentCareCostBeforeDeductible", "urgentCareCostAfterDeductible", "surgeryCostBeforeDeductible", "surgeryCostAfterDeductible"]:
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

