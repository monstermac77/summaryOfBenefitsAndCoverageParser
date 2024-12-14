# pip3 install "camelot-py[base]"
# pip3 install opencv-python
# pip3 uninstall PyPDF2 
# pip3 install PyPDF2==2.12.1
# pip3 install ghostscript
# brew install ghostscript
# still didn't work, and messed up paths stuff so undid
# import camelot
# tables = camelot.read_pdf("summaryOfBenefitsAndCoveragePDFs/2024-2025-aetna-justworks-medical-c3-sbc.pdf")
# tables.export('foo.csv', f='csv', compress=False)

# pip install tika
# then got RuntimeError: Unable to start Tika server
# installed brew
# nano ~/.zshrc and add export PATH=$PATH:/opt/homebrew/bin
# sudo softwareupdate --install-rosetta
# brew tap adoptopenjdk/openjdk
# brew install --cask adoptopenjdk8
from tika import parser 
import re
raw = parser.from_file("summaryOfBenefitsAndCoveragePDFs/2024-2025-aetna-justworks-medical-c3-sbc.pdf")['content']

def replace_multiple_spaces(input_string):
    return re.sub(r'\s+', ' ', input_string).strip()

def getNumberFromString(string):
     string = string.replace(",", "")
     return re.findall(r'\d+', string)[0]

rawStripped = replace_multiple_spaces(raw.replace("\n", " "))
deductibleSection = rawStripped.split("What is the overall deductible?")[1].split("Are there services covered before")[0]
reduced = deductibleSection.split(" Out")[0]
if ":" in reduced:
	reduced = reduced.split(":")[1]
if "/" in reduced:
    reduced = reduced.split("/")[0]
print(getNumberFromString(reduced))
