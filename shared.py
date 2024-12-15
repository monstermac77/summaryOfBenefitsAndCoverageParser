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