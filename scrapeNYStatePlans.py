import pprint
import requests
import json
# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

marketplace = "individual" # employer/individual
zipCode = "10001" # 10001/10012
year = "2025" # 2024/2025

print(f"Searching the {marketplace} marketplace with zip {zipCode} for year {year}")

def getPlansFromSearch(soup):
	plans = soup.findAll("input", {"class" : "planSelect"})
	ids = [plan['id'] for plan in plans]
	return ids

def getPlan(session, formUID, CSRFToken, type, identifier):
	
	print("Getting plan", identifier)

	if type == "individual":

		planID = identifier

		headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
			'accept-language': 'en-US,en;q=0.9',
			'cache-control': 'no-cache',
			'pragma': 'no-cache',
			'priority': 'u=0, i',
			'referer': 'https://nystateofhealth.ny.gov/{}/searchAnonymousPlan/search'.format(marketplace),
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

		url = f"https://nystateofhealth.ny.gov/{marketplace}/searchAnonymousPlan/plan/{planID}?county=New%20York&coverageTier=INDIVIDUAL&entityType=INDIVIDUAL&planYear={year}&youPay="
		print(url)
		response = session.get(
			url,
			headers=headers,
		)

		html = response.content.decode('utf-8')

		# add in the plan URL for the parser
		html = str(html + f"<div id='scrapersLinkToPlan>{url}</div>")

	elif type == "employer":

		planID = identifier["uniqueID"]
		productID = identifier["productID"]

		headers = {
			'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
			'accept-language': 'en-US,en;q=0.9',
			'cache-control': 'no-cache',
			'pragma': 'no-cache',
			'priority': 'u=0, i',
			'referer': 'https://nystateofhealth.ny.gov/employer/shop/search/quotes?includeHNYPlans=&showDental=false&zipCode=',
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

		# params = [
		# 	('enrollmentSetupId', ''),
		# 	('cPlanIds', ''),
		# 	('cUniquePlanIds', ''),
		# 	('cUniquePlanIdsWithCounty', ''),
		# 	('carrier', ''),
		# 	('coverageTier', ''),
		# 	('metal_type', ''),
		# 	('sortPlans', ''),
		# 	('showDental', 'false'),
		# 	('retainFilter', 'true'),
		# 	('formUID', formUID),
		# 	('CSRFToken', CSRFToken),
		# 	('zipCode', zipCode),
		# 	('includeHNYPlans', 'false'),
		# 	('enrollmentSetupId', ''),
		# ]
		
		url = 'https://nystateofhealth.ny.gov/employer/shop/search/plan/{}/{}/{}NEW%20YORK'.format(productID, planID, planID)
		response = session.get(
			url,
			# params=params,
			headers=headers,
		)

		html = response.content

	with open("plans/automated/" + marketplace + "_" + year + "_" + str(planID) + ".html", "wb") as file:
		file.write(html)

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

response = session.get('https://nystateofhealth.ny.gov/{}/'.format(marketplace), params=params, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")
form = soup.find("form", {"id" : "formInstantQuotes"})
formUID = form.find("input" , {"name" : "formUID"})['value']
CSRFToken = form.find("input" , {"name" : "CSRFToken"})['value']
print("Got homepage, posting zip code.")

# post the zip code

headers = {
	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	'accept-language': 'en-US,en;q=0.9',
	'cache-control': 'no-cache',
	'content-type': 'application/x-www-form-urlencoded',
	'origin': 'https://nystateofhealth.ny.gov',
	'pragma': 'no-cache',
	'priority': 'u=0, i',
	'referer': 'https://nystateofhealth.ny.gov/{}/?lang=en'.format(marketplace),
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

if marketplace == "individual": 
	url = 'https://nystateofhealth.ny.gov/individual/searchAnonymousPlan/search'
	data = {
		'entityId': '0',
		'zip': zipCode,
		'formUID': formUID,
		'CSRFToken': CSRFToken,
	}
elif marketplace == "employer":
	url = "https://nystateofhealth.ny.gov/employer/home/quotes"
	data = {
		'coverage_type': '1',
		'noOfEmp': '2',
		'insurance_type': '1',
		'zip': zipCode,
		'formUID': formUID,
		'CSRFToken': CSRFToken,
	}


response = session.post(
	url,
	headers=headers,
	data=data,
)
soup = BeautifulSoup(response.content, "html.parser")

formUID = soup.find("input", {"name" : "formUID"})['value']

# get the number of pages with the filter of individual (relevant only for the individual marketplace)
if marketplace == "individual": 
	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'accept-language': 'en-US,en;q=0.9',
		'cache-control': 'no-cache',
		'content-type': 'application/x-www-form-urlencoded',
		# 'cookie': 'compare_plans=; compare_counties=; compare_coverage_tiers=; compare_you_pay=; JSESSIONID=8538-vNkhv30gHRn7hvbi2S56c_SwNwN2wJU4JqU.1dk9ngk4o; cookieEnabled=true',
		'origin': 'https://nystateofhealth.ny.gov',
		'pragma': 'no-cache',
		'priority': 'u=0, i',
		'referer': 'https://nystateofhealth.ny.gov/{}/searchAnonymousPlan/search'.format(marketplace),
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
			year,
			year,
		],
		'searchcoverageTierIndv': 'INDIVIDUAL',
		'coverageTier': 'INDIVIDUAL',
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
		'pageNo': '0',
		'totalPages': '41',
		'isMMCElig': 'false',
		'isCHPElig': 'false',
		'isSilverElig': 'false',
		'isEPElig': 'false',
		'formUID': formUID,
		'CSRFToken': CSRFToken,
	}

	response = session.post(
		'https://nystateofhealth.ny.gov/{}/searchAnonymousPlan/searchPlans'.format(marketplace), 
		headers=headers,
		data=data,
	)
	soup = BeautifulSoup(response.content, "html.parser")
	totalPages = int(soup.find("input", {"id" : "totalPages"})['value']) + 1

elif marketplace == "employer":
	# we're just going to continue the requests until there are no quotes basically
	totalPages = "unknown"
	pass

planIDs = []
print(f"Got total page count with persons covered filter: {totalPages}")

if marketplace == "individual": 
	# we already got page 1?
	for i in range(1, totalPages):

		formUID = soup.find("input", {"name" : "formUID"})['value']

		data = {
			'entityType': 'INDIVIDUAL',
			'searchentityType': 'INDIVIDUAL',
			'dependent29Selected': '',
			'searchcounty': 'NEW YORK',
			'county': 'NEW YORK',
			'planYearTxt': [
				year,
				year,
			],
			'searchcoverageTierIndv': 'INDIVIDUAL', # these needed to be changed
			'coverageTier': 'INDIVIDUAL', # these needed to be changed
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
			'totalPages': totalPages,
			'isMMCElig': 'false',
			'isCHPElig': 'false',
			'isSilverElig': 'false',
			'isEPElig': 'false',
			'formUID': formUID,
			'CSRFToken': CSRFToken,
		}

		response = session.post(
			'https://nystateofhealth.ny.gov/{}/searchAnonymousPlan/pagePlans'.format(marketplace),
			headers=headers,
			data=data,
		)
		soup = BeautifulSoup(response.content, "html.parser")
		# retrieve from the last soup
		
		newIDs = getPlansFromSearch(soup)

		print("Got {} new IDs:".format(len(newIDs)), newIDs)

		planIDs.extend(newIDs)

	
	# now we have all the plans, we need to start actually getting the data
	for id in planIDs:
		getPlan(session, formUID, CSRFToken, "individual", id)

elif marketplace == "employer":

	formUID = soup.find("input", {"name" : "formUID"})['value']

	pageNumber = 0
	plans = []
	while True:
		headers = {
			'accept': 'application/json, text/javascript, */*; q=0.01',
			'accept-language': 'en-US,en;q=0.9',
			'cache-control': 'no-cache',
			'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
			# 'cookie': 'JSESSIONID=6xYxa5dYWX2sIQgfpTAr5Qopl5aA990cOlj7q_lM.1cqjr5ope; cookieEnabled=true',
			'origin': 'https://nystateofhealth.ny.gov',
			'pragma': 'no-cache',
			'priority': 'u=0, i',
			'referer': 'https://nystateofhealth.ny.gov/employer/shop/search/quotes?includeHNYPlans=false&showDental=false&zipCode=10001',
			'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': '"macOS"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-origin',
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
			'x-requested-with': 'XMLHttpRequest',
		}

		data = {
			'zipCode': zipCode,
			'carrier': '',
			'metal_type': '',
			'insuranceType': '1',
			'enrollmentSetupId': '',
			'eId': '',
			'isDental': '',
			'orderOfTotalPremium': '',
			'includeHNYPlansInd': 'false',
			'formUID': formUID,
			'CSRFToken': CSRFToken,
			'pageNumber': pageNumber,
		}

		response = session.post(
			'https://nystateofhealth.ny.gov/employer/shop/search/quotes/filterSearch',
			headers=headers,
			data=data,
		)
		responseJSON = json.loads(response.content)
		quotes = responseJSON["quotes"]
		newPlans = [
			{
				"uniqueID" : quote["plan"]["planUniqueId"],
				"productID" : quote["plan"]["product"]["id"]
			}
			for quote in quotes
		]
		print(f"Found {len(quotes)} plans: {[plan['productID'] for plan in newPlans]}")
		pageNumber += 1
		plans.extend(newPlans)
		if(len(quotes)) == 0:
			break
	
	# now we have all the plans, we need to start actually getting the data
	for plan in plans:
		getPlan(session, formUID, CSRFToken, "employer", plan)






