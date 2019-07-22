from html.parser import HTMLParser
from Course import Course

class qisHTMLParser(HTMLParser):

    state = -1
    # state:
    # -1: no Modul found
    #  0: Modul found, waiting for <b> tag
    #  1: <b> tag found, reading data
 

    def __init__(self):
        self.courses = []
        self.ctr = 0
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'td' and ('class', 'qis_records') in attrs:
            #print(str(attrs))

            if self.state == -1:
                self.courses.append(Course())
                self.state = 0

        elif self.state == 0 and tag == 'b':
            self.state = 1

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if self.state == 1:
            self.state = 0
	
            while data.startswith(" "):
                data = data[1:]

            while data.endswith(" "):
                data = data[:-1]

            if (self.ctr == 0):
                self.courses[-1].modulnr = data
            elif (self.ctr == 1):
                self.courses[-1].name = data
            elif (self.ctr == 2):
                self.courses[-1].sem = data
            elif (self.ctr == 3):
                self.courses[-1].grade = data
            elif (self.ctr == 4):
                self.courses[-1].status = data  
            elif (self.ctr == 5):
                self.courses[-1].ects = data 
            elif (self.ctr == 6):
                self.courses[-1].pArt = data
            elif (self.ctr == 9):
                self.courses[-1].date = data

            self.ctr += 1

            if self.ctr % 10 == 0:
                self.ctr = 0
                self.state = -1

    def getCourses(self):
        return self.courses


"""
parser = qisHTMLParser()
parser.feed('''<td class="qis_records" valign="top" align="right" width="8%">
 		<b>9000&nbsp;</b>
 	</td>
	<td class="qis_records" valign="top" align="left" width="40%">
		 		 	<b>ECTS-Gesamtkonto</b>
		 	</td>
	<td class="qis_records" valign="top" align="left" width="14%">
									<b>&nbsp;WS 17/18</b>
	</td>
	<td class="qis_records" valign="top" align="left" width="9%">
					<b>&nbsp;</b>
			</td>
	<td class="qis_records" valign="top" align="left" width="18%">
					<font>
				 			<b>&nbsp;Prüfung vorhanden</b>
					</font>
	</td>
	<td class="qis_records" valign="top" align="right" width="5%">
								<b>30,0&nbsp;</b>
	</td>
	<td class="qis_records" valign="top" align="left" width="5%">
										<b>&nbspK</b>
	</td>
	<td class="qis_records" valign="top" align="left" width="6%">
		<b></b>
	</td>
	<td class="qis_records" valign="top" align="center" width="6%">
		<b>1</b>
	</td>
	<td class="qis_records" valign="top" align="left" width="10%">
		<b>09.02.2018&nbsp;</b>
	</td>
</tr>''')
"""


