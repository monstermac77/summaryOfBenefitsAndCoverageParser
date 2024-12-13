import pprint
import requests
# pip3 install beautifulsoup4
from bs4 import BeautifulSoup

marketplace = "individual"
#marketplace = "employer"
year = "2025"

def getPlansFromSearch(soup):
	plans = soup.findAll("input", {"class" : "planSelect"})
	ids = [plan['id'] for plan in plans]
	return ids

def getPlan(session, planID):
	
	print("Getting plan", planID)

	headers = {
		'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
		'accept-language': 'en-US,en;q=0.9',
		'cache-control': 'no-cache',
		# 'cookie': 'compare_plans=; compare_counties=; compare_coverage_tiers=; compare_you_pay=; JSESSIONID=Tei_inohhvWuEAKGgdwW_MQLrXyQxWahYr6bEm5v.1cakcsksa; cookieEnabled=true; org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE=en',
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

	params = {
		'county': 'New York',
		'coverageTier': 'INDIVIDUAL',
		'entityType': 'INDIVIDUAL',
		'planYear': year,
		'youPay': '',
	}

	response = session.get(
		'https://nystateofhealth.ny.gov/{}/searchAnonymousPlan/plan/{}'.format(marketplace, planID),
		params=params,
		headers=headers,
	)

	with open("plans/automated/" + marketplace + "_" + year + "_" + str(planID) + ".html", "wb") as file:
		file.write(response.content)
	
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
response = session.get('https://nystateofhealth.ny.gov/{}/'.format(marketplace), params=params, headers=headers)
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

data = {
    'entityId': '0',
    'zip': '10012',
    'formUID': formUID,
    'CSRFToken': CSRFToken,
}

response = session.post(
    'https://nystateofhealth.ny.gov/{}/searchAnonymousPlan/search'.format(marketplace),
    headers=headers,
    data=data,
)
soup = BeautifulSoup(response.content, "html.parser")

formUID = soup.find("input", {"name" : "formUID"})['value']

# get the number of pages
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
planIDs = []

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
	getPlan(session, id)

