class Course:
    modulnr = 0
    name = ""
    sem = ""
    grade = 0.0
    status = ""
    ects = 0.0
    pArt = ""
    date = ""

    def __str__(self):
        return str(self.modulnr) + ' | ' + self.name + ' | ' + self.sem + ' | ' + str(self.grade) + ' | ' + self.status + ' | ' + str(
            self.ects) + ' | ' + str(self.pArt)+ ' | ' + str(self.date)
