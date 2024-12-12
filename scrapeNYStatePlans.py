import pprint
import requests
# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

def getPlansFromSearch(soup):
	pass

# get the homepage
session = requests.Session()

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

params = {
    'lang': 'en',
}


# response = session.get('https://nystateofhealth.ny.gov/employer/', params=params, headers=headers)
response = session.get('https://nystateofhealth.ny.gov/individual/', params=params, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
form = soup.find("form", {"id" : "formInstantQuotes"})
formUID = form.find("input" , {"name" : "formUID"})['value']
CSRFToken = form.find("input" , {"name" : "CSRFToken"})['value']

# post the zip code

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    'origin': 'https://nystateofhealth.ny.gov',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://nystateofhealth.ny.gov/individual/?lang=en',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

data = {
    'entityId': '0',
    'zip': '10012',
    'formUID': formUID,
    'CSRFToken': CSRFToken,
}

response = session.post(
    'https://nystateofhealth.ny.gov/individual/searchAnonymousPlan/search',
    headers=headers,
    data=data,
)
soup = BeautifulSoup(response.content, "html.parser")

# get the number of pages
totalPages = int(soup.find("input", {"id" : "totalPages"})['value'])

for i in range(1, totalPages):

	getPlansFromSearch(soup)
	formUID = soup.find("input", {"name" : "formUID"})['value']

	data = {
		'entityType': 'INDIVIDUAL',
		'searchentityType': 'INDIVIDUAL',
		'dependent29Selected': '',
		'searchcounty': 'NEW YORK',
		'county': 'NEW YORK',
		'planYearTxt': [
			'2025',
			'2025',
		],
		'searchcoverageTierIndv': 'Select',
		'coverageTier': '',
		'searchquality': '',
		'quality': '',
		'searchplanCategory': '',
		'planCategory': '',
		'searchmetal': '',
		'metal': '',
		'searchstdnonstd': '',
		'stdnonstd': '',
		'searchissuerId': '',
		'issuerId': '',
		'searchhiosPlanIdTxt': '',
		'hiosPlanIdTxt': '',
		'_dependentAge29': 'on',
		'_outOfNetwork': 'on',
		'calculatedAptc': '',
		'pageNo': i,
		'totalPages': '41',
		'isMMCElig': 'false',
		'isCHPElig': 'false',
		'isSilverElig': 'false',
		'isEPElig': 'false',
		'formUID': formUID,
		'CSRFToken': CSRFToken,
	}

	response = session.post(
		'https://nystateofhealth.ny.gov/individual/searchAnonymousPlan/pagePlans',
		headers=headers,
		data=data,
	)

	print(response.content)
	exit()

print(totalPages)
exit()


exit()


# go between pages

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'no-cache',
    'content-type': 'application/x-www-form-urlencoded',
    # 'cookie': 'compare_plans=; compare_counties=; compare_coverage_tiers=; compare_you_pay=; JSESSIONID=JrK0rl2gu6YRIG6SbP0kjjC4v53K3Fgb-jqal9nQ.1cahputr2; cookieEnabled=true; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en',
    'origin': 'https://nystateofhealth.ny.gov',
    'pragma': 'no-cache',
    'priority': 'u=0, i',
    'referer': 'https://nystateofhealth.ny.gov/individual/searchAnonymousPlan/search',
    'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
}

data = {
    'entityType': 'INDIVIDUAL',
    'searchentityType': 'INDIVIDUAL',
    'dependent29Selected': '',
    'searchcounty': 'NEW YORK',
    'county': 'NEW YORK',
    'planYearTxt': [
        '2025',
        '2025',
    ],
    'searchcoverageTierIndv': 'Select',
    'coverageTier': '',
    'searchquality': '',
    'quality': '',
    'searchplanCategory': '',
    'planCategory': '',
    'searchmetal': '',
    'metal': '',
    'searchstdnonstd': '',
    'stdnonstd': '',
    'searchissuerId': '',
    'issuerId': '',
    'searchhiosPlanIdTxt': '',
    'hiosPlanIdTxt': '',
    '_dependentAge29': 'on',
    '_outOfNetwork': 'on',
    'calculatedAptc': '',
    'pageNo': '1',
    'totalPages': '41',
    'isMMCElig': 'false',
    'isCHPElig': 'false',
    'isSilverElig': 'false',
    'isEPElig': 'false',
    'formUID': '63381',
    'CSRFToken': 'd6aee0b3-0fab-45ba-ade5-66f142359ee9',
}

response = session.post(
    'https://nystateofhealth.ny.gov/individual/searchAnonymousPlan/pagePlans',
    headers=headers,
    data=data,
)

print(response.content)
exit()

# $(".comparePlan-tabs").click() to open everything

# TODO: could improve the gathering of the HTML for sure, probably automate it, but the javascript loading of the page makes it hard
# it returns you to the fucking first page every time you click on one, so it makes sense to basically open 41 tabs I guess and click on the right one and then save?

def parsePlan(htmlPath):

	html = open(htmlPath).read()
	soup = BeautifulSoup(html, "html.parser")

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

	fields = {
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

	# clean it up a bit
	for key, value in fields.items():
		fields[key] = value.strip().replace("$", "")

	#pprint.pprint(fields)

	# parse it out a bit
	finalFields = {}
	for key, value in fields.items():
		if "Raw" not in key:
			# straightforward
			finalFields[key] = value
		else:
			costName = key.replace("Raw", "")
			# if it's a numberical value, then it's very straightforward 
			if is_numerical(value):
				finalFields[costName+"BeforeDeductible"] = finalFields[costName+"AfterDeductible"] = value.strip()
			else:
				# there's some sort of difference
				if "Copay after deductible" in value:
					raw = value.replace("Copay after deductible", "")
					finalFields[costName+"BeforeDeductible"] = "FULL CHARGE"
					finalFields[costName+"AfterDeductible"] = raw.strip()
				if "Coinsurance after deductible" in value:
					raw = value.replace("Coinsurance after deductible" , "")
					processed = float(raw.strip().replace("%", "")) / 100
					finalFields[costName+"BeforeDeductible"] = "FULL CHARGE"
					finalFields[costName+"AfterDeductible"] = "PARTIAL CHARGE: {}".format(processed)
				if "No Charge after deductible" in value:
					finalFields[costName+"BeforeDeductible"] = "FULL CHARGE"
					finalFields[costName+"AfterDeductible"] = "0"
				if "No Charge" == value:
					finalFields[costName+"BeforeDeductible"] = "0"
					finalFields[costName+"AfterDeductible"] = "0"

	#pprint.pprint(finalFields)

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
	for column in ["carrier", "plan", "link", "level", "premium", "deductible", "outOfPocketMax", "therapyCostBeforeDeductible", "therapyCostAfterDeductible", "specialistCostBeforeDeductible", "specialistCostAfterDeductible", "primaryCareCostBeforeDeductible", "primaryCareCostAfterDeductible", "bloodDrawCostBeforeDeductible", "bloodDrawCostAfterDeductible", "psychiatristCostBeforeDeductible", "psychiatristCostAfterDeductible", "urgentCareCostBeforeDeductible", "urgentCareCostAfterDeductible", "surgeryCostBeforeDeductible", "surgeryCostAfterDeductible"]:
		value = finalFields[column]

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

for file in glob.glob("plans/*.html"):
	parsePlan(file)


