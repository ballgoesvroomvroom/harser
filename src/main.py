## lightweight and simple parser for markdown contents to be translated into html document
import os

from regexObj import Regex as RegexObjects
import elements as Elements

"""
TO-DO

All-cleared :)
"""

def warn(*msg, sep=" "):
	## outputs a warning, highlighted by its suffix "[ WARNING ]"
	print("[ WARNING ]:", *msg, sep=sep)

class SubParser:
	## parses contents for a SINGLE article object
	def __init__(self):
		self.root = Elements.Article()

		## should only contains elements whose .createsNewScope attribute is True
		self.currentContainer = [self.root] ## append to the list as it traverses deeper down

	def addContainer(self, container):
		self.currentContainer.append(container)

	def closeContainer(self):
		## close the current container (by removing it from the .currentContainer)
		self.currentContainer.pop()

	def collapseContainer(self, collapseTo=1):
		## collapseTo = 1; collapses all containers until only 1 parent is left, the root element
		## collapseTo -- collapse container until container size hits this number
		for i in range(len(self.currentContainer) -1, collapseTo, -1):
			self.currentContainer.pop()

	def matchLine(self, line):
		## if line is empty, skip it
		if len(line) == 0:
			return

		## check if context is a code block
		if isinstance(self.currentContainer[-1], Elements.CodeBlock):
			## add content directly into codeblock
			warn("in code block")

			## check if it is closing tag
			if RegexObjects.codeblock.match(line):
				## escape code block
				self.closeContainer()
			else:
				warn("added content:", line)
				self.currentContainer[-1].addContent(line)
			return
		else:
			codeblock = RegexObjects.codeblock.match(line)
			if codeblock:
				warn("matched codeblock")
				## create new codeblock
				codeblockObj = Elements.CodeBlock()
				self.currentContainer[-1].addChildren(codeblockObj)
				self.addContainer(codeblockObj)
				return

		## match for list next; check if current container is a list
		list_ele = RegexObjects.list_ele.match(line)
		print("LIST", list_ele)
		if isinstance(self.currentContainer[-1], Elements.ListContainer):
			print("YEP")
			if list_ele:
				## is a list element, add it and move on to the next line
				listObj = Elements.ListItem()

				listObj.content = list_ele.groups()[0]
				self.currentContainer[-1].addChildren(listObj)
				return
			else:
				## next line is not a list content
				## exit list and continue with the remaining matching
				self.closeContainer()
		elif list_ele:
			## current container is not a list
			listContainerObj = Elements.ListContainer()

			## create actual list element object
			listObj = Elements.ListItem()
			listObj.content = list_ele.groups()[0]
			listContainerObj.addChildren(listObj)

			self.currentContainer[-1].addChildren(listContainerObj)
			self.addContainer(listContainerObj)
			return

		## start of actual matching for different tags
		header = RegexObjects.header.match(line)
		if header:
			hashtags, chaptername, articleid = header.groups()
			if len(hashtags) == 1:
				## header 1; regex captured with article id
				self.root.id = articleid ## change id of article element
			else:
				## articleid would be None
				pass

			section = Elements.Section(c="root-section")

			headerObj = Elements.Header()
			headerObj.content = chaptername
			headerObj.headerType = len(hashtags)
			section.addChildren(headerObj)

			self.collapseContainer(1) ## escape back to root
			self.currentContainer[-1].addChildren(section)
			self.addContainer(section)
			return
		img = RegexObjects.image.match(line)
		print(line, img)
		if img:
			alttext, src, caption = img.groups()

			## create new figure instance to wrap image
			figure = Elements.Figure()

			imageObj = Elements.Image()
			imageObj.content = src
			imageObj.alt = alttext

			figcaption = Elements.Figcaption()
			figcaption.content = caption

			figure.addChildren(imageObj, figcaption)

			self.currentContainer[-1].addChildren(figure)
			return
		link = RegexObjects.links.match(line)
		if link:
			text, path = link.groups()

			linkObj = Elements.Link()
			linkObj.content = path
			linkObj.text = text

			self.currentContainer[-1].addChildren(linkObj)
			return
		directed_div = RegexObjects.directed_div.match(line)
		if directed_div:
			dir = directed_div.groups()[0]

			divObject = Elements.Div()
			divObject.addClass("content-container")
			if dir == "l-r":
				## left-right
				divObject.addClass("left-right")
			elif dir == "r-l":
				## right-left
				divObject.addClass("right-left")
			else:
				warn("Defined direction is invalid; input:", dir)

			self.currentContainer[-1].addChildren(divObject)
			self.addContainer(divObject) ## add container
			return
		normal_div = RegexObjects.normal_div.match(line)
		if normal_div:
			divObject = Elements.Div()

			self.currentContainer[-1].addChildren(divObject)
			self.addContainer(divObject)
			return
		closing_div = RegexObjects.closing_div.match(line)
		if closing_div:
			self.closeContainer()
			return
		div_header = RegexObjects.div_header.match(line)
		if div_header:
			headerLevel, heading = div_header.groups()

			headerObj = Elements.Header()
			headerObj.headerType = len(headerLevel)
			headerObj.content = heading

			self.currentContainer[-1].addChildren(headerObj)
			return
		file_upload = RegexObjects.file_upload.match(line)
		if file_upload:
			dispname, filedesc, filepath = file_upload.groups()

			divObject = Elements.Div(c="fileupload")

			file_icon = Elements.Image()
			file_icon.content = "img/includes/text-file.webp"
			file_icon.alt = "icon of .txt files"

			innerDiv = Elements.Div(c="fileupload-text")

			dispname_p = Elements.Para(c="fileupload-header")
			dispname_p.content = dispname
			desc_p = Elements.Para("fileupload-desc")
			desc_p.content = filedesc

			innerDiv.addChildren(dispname_p, desc_p)

			buttonObj = Elements.Button()
			divObject.addChildren(file_icon, innerDiv, buttonObj)
			self.currentContainer[-1].addChildren(divObject)
			return

		## nothing matched; treat it as a regular paragraph
		# ## append line to current paragraph (if any) along with addition of br tags
		# if isinstance(self.currentContainer[-1].children[-1], Elements.Para):
		# 	## add content
		# 	paraObj = self.currentContainer[-1].children[-1]
		# 	paraObj.content += "<br>\n" +line
		# else:
		paraObj = Elements.Para()
		paraObj.content = line
		self.currentContainer[-1].addChildren(paraObj)

class Parser:
	def __init__(self, content):
		self.subparsers = [] ## stores the subparser instances
		self.content = content
		self.parsedContent = "" ## caches parsed contents here

		## states
		self.isActive = False ## triggered whenever the first article object is created
		self.isParsed = False

	def createArticle(self):
		## let the sub parser handle it
		self.subparsers.append(SubParser())
		self.isActive = True

	def lex(self):
		## not really a lexer, but i guess it counts??
		## takes the string contents and builds a hierarchy map along with the addition of tags (semi-parsed at the end)
		lines = self.content.split("\n")

		for linec in range(len(lines)):
			## ignore any meaningless data that may be possibly at the start
			line = lines[linec]

			## look for header
			header = RegexObjects.header.match(line)
			if header and len(header.group(1)) == 1:
				## header 1; the start of a new article
				self.createArticle()
				self.subparsers[-1].matchLine(line)
			elif self.isActive:
				self.subparsers[-1].matchLine(line)
			else:
				## irrelevant content
				pass

	def parse(self, indentLevel=0):
		self.parsedContent = ""
		for article in self.subparsers:
			self.parsedContent += "{}\n".format(article.root.parse(indentLevel))

		self.parsedContent = self.parsedContent[:-1] ## strip trailing line feed
		return self.parsedContent

if __name__ == "__main__":
	input_folder = os.path.dirname(os.path.dirname(__file__))
	d = ""
	with open(os.path.join(input_folder, "input.txt"), "r") as f:
		d = f.read()

	p = Parser(d)
	p.lex()

	with open(os.path.join(input_folder, "o.html"), "w") as f:
		f.write(p.parse(3))

	print("DONE")
