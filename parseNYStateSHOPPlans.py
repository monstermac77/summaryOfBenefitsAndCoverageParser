# pip3 install beautifulsoup4 --break-system-packages
from bs4 import BeautifulSoup
# pip3 install lxml --break-system-packages
from lxml import etree
import pprint

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

# parse it out a bit
finalFields = {}
for key, value in fields.items():
	if "Raw" not in key:
		# straightforward
		finalFields[key] = value
	else:
		costName = key.replace("Raw", "")
		# if it's a numberical value, then it's very straightforward 
		if all([word not in value for word in ["Copay", "deductible"]]):
			finalFields[costName+"BeforeDeductible"] = finalFields[costName+"AfterDeductible"] = value
		else:
			# there's some sort of difference
			if "Copay after deductible" in value:
				raw = value.replace("Copay after deductible", "")
				finalFields[costName+"BeforeDeductible"] = "FULL CHARGE"
				finalFields[costName+"AfterDeductible"] = raw

pprint.pprint(finalFields)

finalString = ""
for column in ["carrier", "plan", "link", "level", "premium", "deductible", "outOfPocketMax", "therapyCostBeforeDeductible", "therapyCostAfterDeductible", "specialistCostBeforeDeductible", "specialistCostAfterDeductible", "primaryCareCostBeforeDeductible", "primaryCareCostAfterDeductible", "blooddrawCostBeforeDeductible", "blooddrawCostAfterDeductible", "psychiatristCostBeforeDeductible", "psychiatristCostAfterDeductible", "urgentCareCostBeforeDeductible", "urgentCareCostAfterDeductible", "surgeryCostBeforeDeductible", "surgeryCostAfterDeductible"]:
	finalString += finalFields[column] + ", "


print(finalString)


