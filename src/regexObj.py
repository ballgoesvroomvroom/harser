import re

class Regex:
	## .group(1) is hashtags captured
	## .group(2) is chapter name captured
	## .group(3) is article id
	header = re.compile("^(#{1,6}) (.*?)(?: \[(.*)\])?$")

	## use to capture images
	## .group(1) is the image alt text
	## .group(2) is the image src path
	## .group(3) is the image caption (figcaption contents)
	image = re.compile("^!\[(.*?)\]\((.*?)\)\[(.*?)\]$")

	## .group(1) is the link text
	## .group(2) is the link path
	links = re.compile("\[(.*?)\]\((.*?)\)")

	## use to replace backticks with <code> tags
	code = re.compile("`([^`]+?)`")

	## code block; multi-line code block
	codeblock = re.compile("^```$")

	## denotes a new div
	## .group(1) is the direction "l-r" or "r-l"
	directed_div = re.compile("^{ \[(\w-\w)\]$")

	## denotes a new plain div
	normal_div = re.compile("^{$")

	## denotes a closure of div
	closing_div = re.compile("^}$")

	## captures a header for a div; used when there is no need to create a section
	## .group(1) returns the hashtags corersponding to the header level
	## .group(2) returns the actual header content
	div_header = re.compile(r"^(?<!\\){ *(#{1,6})([^ ]+) *}$")

	## captures a list element
	## .group(1) is the list element's content
	list_ele = re.compile(r"^(?<!\\)- (.*)$")

	## captures a file upload element (custom)
	## group 1 returns file name (to be displayed)
	## group 2 returns file description
	## group 3 returns file path stored (along with the file extension of course)
	file_upload = re.compile("{(.*?)}\[(.*?)\]\((.*?)\)")

	### REPLACEMENTS FOR _safeParse
	## to capture ampersand tags
	amp = re.compile("&(?!nbsp;)")

	## to capture arrow brackets
	left_arrowbracket = re.compile("<(?!br>)")
	right_arrowbracket = re.compile("(?<!<br)>")
