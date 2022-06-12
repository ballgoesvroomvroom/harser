import constants
from regexObj import Regex as RegexObjects

INDENT = constants.INDENT

class Element:
	hasClosingTag = True
	createsNewScope = False ## whether children is indented
	def __init__(self, c="", id=""):
		self.children = []
		self.parent = None ## will be added when passed as argument into another object's .addChildren method

		self.c, self.id = c, id

		self.content = ""

	def addChildren(self, *childrenObjects):
		## childrenObject being an object whose base class is Element
		## can only be added if element called on (self) has a closing tag
		if not self.createsNewScope:
			raise RuntimeError("Unable to give elements whose property '.createsNewScope' is False")
		else:
			for children in (childrenObjects):
				self.children.append(children)
				children.parent = self ## modify parent's parent

	def addClass(self, className):
		if len(self.c) == 0:
			## no previous content
			self.c = className
		else:
			## has previous content
			self.c += " " +className

	def addId(self, id):
		self.id = id

	## inline parsing
	def _wrapBackticks(self, text):
		return RegexObjects.code.sub(r"<code>\1</code>", text)

	def _wrapLinks(self, text):
		return RegexObjects.links.sub(r'<a href="\2">\1</a>', text)

	def _safeParse(self, text):
		## replaces "<", ">" and "&"
		text = RegexObjects.left_arrowbracket.sub("&lt;", text)
		text = RegexObjects.right_arrowbracket.sub("&gt;", text)
		return RegexObjects.amp.sub("&amp;", text)

	def parseChildren(self, parentIndentLevel):
		## iterate through children and parses them
		children = ""
		for childrenObj in self.children:
			children += childrenObj.parse(parentIndentLevel +1) +"\n"
		return children[:-1] ## remove trailing whitespace

class Article(Element):
	## root element for storing
	type = -1
	createsNewScope = True

	def parse(self, indentLevel=0):
		header = INDENT *indentLevel +"<article id=\"{}\" class=\"{}\">\n".format(self.id, self.c)
		return header +self.parseChildren(indentLevel) +"\n" +(INDENT *indentLevel) +"</article>"

class Section(Element):
	type = 0
	createsNewScope = True

	def parse(self, indentLevel=0):
		header = INDENT *indentLevel +"<section id=\"{}\" class=\"{}\">\n".format(self.id, self.c)
		return header +self.parseChildren(indentLevel) +"\n" +INDENT *indentLevel +"</section>"

class Div(Element):
	type = 1
	createsNewScope = True

	def parse(self, indentLevel=0):
		header = INDENT *indentLevel +"<div class=\"{}\" id=\"{}\">\n".format(self.c, self.id)

		children = self.parseChildren(indentLevel)		

		return header +children +"\n" +INDENT *indentLevel +"</div>"

class Para(Element):
	type = 2

	def _parseInline(self):
		self.content = self._safeParse(self.content)

		## adds actual html tags, call ._safeParse(content) before
		self.content = self._wrapBackticks(self.content)
		self.content = self._wrapLinks(self.content)

	def parse(self, indentLevel=0):
		self._parseInline()

		return INDENT *indentLevel +"<p id=\"{}\" class=\"{}\">{}</p>".format(self.id, self.c, self.content)

class Header(Element):
	type = 3

	## specific attributes
	headerType = 1 ## headerType == 1; h1 tag; till headerType == 6; h6 tag

	def parse(self, indentLevel=0):
		return INDENT *indentLevel +"<h{} id=\"{}\" class=\"{}\">\n{}{}\n{}</h{}>".format(self.headerType, self.id, self.c, INDENT *(indentLevel +1), self.content, INDENT *indentLevel, self.headerType)

		# children = self.parseChildren(indentLevel)
		# if len(children) == 0:
		# 	return header +(INDENT *indentLevel) +"</h{}>".format(self.headerType)
		# else:
		# 	return header +self.parseChildren(indentLevel) +"\n" +INDENT *indentLevel +"</h{}>".format(self.headerType)

class Image(Element):
	type = 4
	hasClosingTag = False

	## specific attributes
	alt = ""

	def parse(self, indentLevel=0):
		## self.content being the src for the image
		return INDENT *indentLevel +"<img class=\"{}\" id=\"{}\" src=\"{}\" alt=\"{}\">".format(self.c, self.id, self.content, self.alt)

class Link(Element):
	type = 5
	createsNewScope = True

	## specific attributes
	text = ""

	def parse(self, indentLevel=0):
		## self.content being the actual destination link
		header =  INDENT *indentLevel +"<a class=\"{}\" id=\"{}\" href=\"{}\">\n{}{}".format(self.c, self.id, self.content, INDENT *(indentLevel +1), self.text)
		return header +self.parseChildren(indentLevel) +"\n" +INDENT *indentLevel +"</a>"

class Figure(Element):
	type = 6
	createsNewScope = True

	def parse(self, indentLevel=0):
		header = INDENT *indentLevel +"<figure class=\"{}\" id=\"{}\">\n".format(self.c, self.id)

		return header +self.parseChildren(indentLevel) +"\n" +INDENT *indentLevel +"</figure>"

class Figcaption(Element):
	## added into Figure
	type = 7

	def parse(self, indentLevel=0):
		## self.content being the caption
		return INDENT *indentLevel +"<figcaption>{}</figcaption>".format(self.content)

class CodeBlock(Element):
	type = 8
	createsNewScope = True

	## specific attributes
	code_contents = [] ## multi-line

	def addContent(self, line):
		## adds the line as a raw content (no parsing done to line)
		self.code_contents.append(line)

	def parse(self, indentLevel=0):
		return INDENT *indentLevel +"<pre><code>{}</code></pre>".format("\n".join(self.code_contents))

class ListContainer(Element):
	type = 9
	createsNewScope = True

	## specific attributes
	listType = "ul" ## unordered list // "ol": "ordered list"

	def parse(self, indentLevel=0):
		header = INDENT *indentLevel +"<{} id=\"{}\" class=\"{}\">\n".format(self.listType, self.id, self.c)
		return header +self.parseChildren(indentLevel) +"\n" +"{}</{}>".format(INDENT *indentLevel, self.listType)

class ListItem(Element):
	type = 10

	def parse(self, indentLevel=0):
		## self.content is the actual list content
		return INDENT *indentLevel +"<li id=\"{}\" class=\"{}\">{}</li>".format(self.id, self.c, self.content)

class Button(Element):
	type = 11
	createsNewScope = True

	def parse(self, indentLevel=0):
		header = INDENT *indentLevel +"<button id=\"{}\" class=\"{}\">".format(self.id, self.c)

		children = self.parseChildren(indentLevel)
		if len(children) == 0 and len(self.content) == 0:
			return header +"</button>"
		elif len(children) == 0 and len(self.content) > 0:
			return header +"\n{}\n{}</button>".format(self.content, INDENT *indentLevel)
		else:
			return header +"\n{}\n{}\n{}</button>".format(self.content, self.parseChildren(indentLevel), INDENT *indentLevel)