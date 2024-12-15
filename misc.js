// helping gather links from a page to scrape (pdfs)
var links = "";
$(".download-link").each(function(index, element) {
	links += $(this).find("a").attr("href") + ".pdf, ";
});
links = links.slice(0, -2);
console.log(links);
// 