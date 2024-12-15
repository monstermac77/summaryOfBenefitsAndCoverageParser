def is_numerical(value):
	
	# remove dollar signs
	value = value.replace("$", "")
	
	# Check if the cleaned string is a valid numeric string
	try:
		float(value)
		return True
	except ValueError:
		return False

def getCarrier(text):
	if "emblemhealth.com" in text:
		return "Emblem Health"
	elif "UnitedHealthcare.png" in text or "UnitedHealthcare" in text:
		return "United Healthcare"
	elif "anthem.com" in text:
		return "Anthem"
	elif "hioscar.com" in text:
		return "Oscar"
	elif "healthfirst.org" in text:
		return "Healthfirst"
	elif "fideliscare.org" in text:
		return "Ambetter from Fidelis Care"
	elif "metroplus.org" in text:
		return "MetroPlusHealth"
	elif "aetna.com" in text:
		return "Aetna"
	return "Could not determine carrier"

def cleanPlan(plan, dataSource):
	for key, value in plan.items():
		if value == None: continue
		plan[key] = value.strip().replace("$", "")
	return plan

def processPlan(plan, dataSource):

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
				elif "no charge" in value.lower():
					processedPlan[costName+"BeforeDeductible"] = "0"
					processedPlan[costName+"AfterDeductible"] = "0"
				elif "%" in value:
					# it's just flat co-insurance
					processed = float(value.strip().replace("%", "")) / 100
					processedPlan[costName+"BeforeDeductible"] = "PARTIAL CHARGE: {}".format(processed)
					processedPlan[costName+"AfterDeductible"] = "PARTIAL CHARGE: {}".format(processed)
	
	return processedPlan


def printPlan(plan, source):

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

	finalString = '"{}", '.format(source)

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
		if value is None: 
			finalString += "TODO, "
		elif value == "FULL CHARGE": 
			finalString += "=" + chosenPair + ", "
		elif "PARTIAL CHARGE: " in value:
			coinsurance = value.replace("PARTIAL CHARGE: ", "")
			finalString += "={}*{}".format(chosenPair, coinsurance) + ", "
		else:
			finalString += '"{}", '.format(value)
	finalString = finalString.rstrip(", ")

	print(finalString)


# statically defined
def getPremiumForPlan(identifier):
	map = {
		"2024-2025-aetna-justworks-medical-c3-sbc.pdf": "$530", 
		"2024-2025-aetna-justworks-medical-b3-sbc.pdf": "$579", 
		"2024-2025-aetna-justworks-medical-d1-sbc.pdf": "$449", 
		"2024-2025-aetna-justworks-medical-h3-sbc.pdf": "$433", 
		"2024-2025-aetna-justworks-medical-h2-sbc.pdf": "$416", 
		"2024-2025-aetna-justworks-medical-g6-sbc.pdf": "$621", 
		"2024-2025-aetna-justworks-medical-c2-sbc.pdf": "$530", 
		"2024-2025-aetna-justworks-medical-g4-sbc.pdf": "$658", 
		"2024-2025-aetna-justworks-medical-f4-sbc.pdf": "$638", 
		"2024-2025-aetna-justworks-medical-d2-sbc.pdf": "$428", 
		"2024-2025-aetna-justworks-medical-d3-sbc.pdf": "$447", 
		"2024-2025-aetna-justworks-medical-h1-sbc.pdf": "$558", 
		"2024-2025-aetna-justworks-medical-a7-sbc.pdf": "$560", 
		"2024-2025-aetna-justworks-medical-g5-sbc.pdf": "$697", 
		"2024-2025-aetna-justworks-medical-h4-sbc.pdf": "$420", 
		"2024-2025-aetna-justworks-medical-b4-sbc.pdf": "$656", 
		"2024-2025-aetna-justworks-medical-b5-sbc.pdf": "$525", 
		"2024-2025-aetna-justworks-medical-c5-sbc.pdf": "$552", 
		"2024-2025-aetna-justworks-medical-f1-sbc.pdf": "$766", 
		"2024-2025-aetna-justworks-medical-g1-sbc.pdf": "$609", 
		"2024-2025-aetna-justworks-medical-a8-sbc.pdf": "$531", 
		"2024-2025-aetna-justworks-medical-j1-sbc.pdf": "$360", 
		"2024-2025-aetna-justworks-medical-f3-sbc.pdf": "$670", 
		"2024-2025-aetna-justworks-medical-f2-sbc.pdf": "$757", 
		"2024-2025-aetna-justworks-medical-g2-sbc.pdf": "$481"
	}
	return map[identifier]