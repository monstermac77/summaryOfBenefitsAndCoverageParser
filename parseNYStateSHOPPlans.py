# pip3 install beautifulsoup4 --break-system-packages
from bs4 import BeautifulSoup
# pip3 install lxml --break-system-packages
from lxml import etree

# $(".comparePlan-tabs").click() to open everything

html = open("plans/plan.html").read()
soup = BeautifulSoup(html, "html.parser")

def getCarrier(html):
	if "emblemhealth.com" in html:
		return "Emblem Health"
	return "Could not determine carrier"


root = etree.HTML(html)
plan = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/div[1]/div/div/h5')[0].text
carrier = getCarrier(html)
link = "https://nystateofhealth.ny.gov" + soup.find("form", {"id" : "backToComparePlan"}).get('action')
# note: for some reason had to remove the tbody's in these for them to work, copied full xpath from Chrome
metalLevel = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/div[1]/table/tr[1]/td[2]')[0].text
premium = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/table[1]/tr[1]/td[2]/span')[0].text
deductible = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/table[1]/tr[3]/td[2]/span')[0].text.strip()
outOfPocketMax = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/table[1]/tr[4]/td[2]/span')[0].text.strip()

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

columns = [
	
]

print(genericDrugsRaw)
exit()




elements = root.xpath('/html/body/div/div[4]/div/div/div/form[1]/table[1]/tr[1]/td[2]/span')
for element in elements:
    print(element.text)  # This should print 'Target Data'
exit()
metalLevel = soup.find("table", {"id" : "planDataTop"}).find("tr").findAll("td")[1].text
print(metalLevel)

# print(plan, carrier, link)