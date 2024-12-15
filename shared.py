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