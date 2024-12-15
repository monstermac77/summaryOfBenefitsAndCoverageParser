// helping gather links from a page to scrape (pdfs)
// var links = "";
var links = [];
$(".download-link").each(function(index, element) {
	// links += $(this).find("a").attr("href") + ".pdf, ";
	links.push($(this).find("a").attr("href") + ".pdf");
});
// links = links.slice(0, -2);
console.log(links);

// Function to open and download a single file in a new tab
const openAndDownloadPDF = (url) => {
	// Open the URL in a new tab
	window.open(url, '_blank');
};

// Iterate over the list and open each file in a new tab
links.forEach(link => {
	openAndDownloadPDF(link);
});