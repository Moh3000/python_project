# Pandas used as dataframe to manipulate the files efficiently
import pandas as pd
from Filter import *
from fuzzywuzzy import fuzz
import os
from Taker import *
import re
from datetime import *


# Class definition
class AttendanceTaker(Taker):

    # Constructer
    def __init__(self, studentListPath, attendnaceReportsPath, participationReportsPath, outputPath, minimumDuration, dropFirst, dropLast):
        # The following are input to the class
        self.__studentListPath = studentListPath
        self.__attendnaceReportsPath = attendnaceReportsPath
        self.__participationReportsPath = participationReportsPath
        self.__outputPath = outputPath
        self.__minimumDuration = minimumDuration
        self.__dropFirst = dropFirst
        self.__dropLast = dropLast

        # The following are outputs of the class
        self.__attendanceSheet = None
        self.__participationSheet = None
        self.__nonValidAR = None
        self.__nonValidPR = None

    # Overriding the load students method
    def loadStudents(self):
        # Loading the students list into pandas dataframe
        self.__studentList = pd.read_csv(self.__studentListPath, header=0, names=["Student Id", "Student Name"])
        self.__studentList["Student Id"] = self.__studentList["Student Id"].apply(str)
        # Adding column that contains the first and last name of each student
        self.__studentList["FirstLastName"] = self.__studentList['Student Name'].apply(lambda x:
                                                                         x.strip().split(" ")[0] + " " +
                                                                         x.strip().split(" ")[3])

        self.__studentList = self.__studentList.set_index('FirstLastName')

    # Overriding the take attendance method
    def takeAttendance(self):

        # nonValidAR is a dictionary that contains non-valid attendance reports entries
        self.__nonValidAR = {}

        # Creating a dataframe for saving attendance results
        self.__attendanceSheet = pd.DataFrame()
        self.__attendanceSheet["Student ID"] = self.__studentList["Student Id"]
        self.__attendanceSheet["Student Name"] = self.__studentList['Student Name']

        # get the course code
        courseCode = getCourseCode(self.__studentListPath)

        # List to store all files names
        fileList = []

        # Get all meeting attendance reports files
        for root, dirs, files in os.walk(self.__attendnaceReportsPath):
            for file in files:
                # Check whether the file corresponds to the course specified
                if file.find(courseCode) != -1:
                    fileList.append(f"{self.__attendnaceReportsPath}/{file}")

        # Iterate through all attendance meeting reports
        for attendanceReport in fileList:

            # Get the report date
            reportDate = getReportDate(attendanceReport)

            # Add the report date to the attendance sheet, all student are assumed to be absent at first
            self.__attendanceSheet[reportDate] = "a"

            # Open the attendance meeting report using pandas data frame
            df = pd.read_csv(attendanceReport, header=0, names=["Name", "Duration"])

            # Copy the original name for each student before filtering
            df["Name (Original Name)"] = df["Name"]

            # Cleaning the names from non-alphanumeric characters
            df["Name"] = df["Name"].apply(lambda x: removeNonAlphanumeric(x))

            # extracting student id number from each row if exists
            df["Student Id"] = df["Name"].apply(lambda x: extractNumbers(x) if len(extractNumbers(x)) == 7 else "Not valid")

            # Removing numbers from names
            df["Name"] = df["Name"].apply(lambda x: removeNumbers(x))
            df = df.set_index("Name")

            # Remove any student who didn't attend the minimum duration
            df = df[df["Duration"] > self.__minimumDuration]

            # Creating dataframe for non-valid meeting attendance reports
            self.__nonValidAR[reportDate] = pd.DataFrame(df)

            # Drop student id column from the non-valid report
            self.__nonValidAR[reportDate] = self.__nonValidAR[reportDate].drop(["Student Id"], axis = 1)

            # Creating a smiliarity matrix
            similarityMatrix = pd.DataFrame(columns = self.__studentList.index, index = df.index)

            # Iterating through the similarity matrix
            for row in df.index:
                for column in self.__studentList.index:
                    # Calculating similarity between names in student list and names in meeting attendance report
                    similarityMatrix.loc[row, column] = fuzz.ratio(row.lower(), column.lower())
            # pd.set_option('display.max_rows', None)
            # pd.set_option('display.max_columns', None)
            # pd.set_option('display.width', None)
            # pd.set_option('display.max_colwidth', -1)

            # Convert entries into numeric in order to compare them
            similarityMatrix[similarityMatrix.columns] = similarityMatrix[similarityMatrix.columns].apply(pd.to_numeric)

            # Iterating through pairs of maximum similarity
            for maxSimilarity in similarityMatrix.idxmax().index:
                # Extracting the pairs of students
                studentFromStudentList = maxSimilarity
                studentFromMeetingReport = similarityMatrix.idxmax()[maxSimilarity]

                # If the similarity between names is >= 60 and between ids = 100 then the student is considered attended
                if similarityMatrix.loc[studentFromMeetingReport, studentFromStudentList] >= 60 and\
                        fuzz.ratio(df.loc[studentFromMeetingReport, "Student Id"], self.__studentList.loc[studentFromStudentList, "Student Id"]) == 100:
                    # Assign attended for the student in that date
                    self.__attendanceSheet.loc[studentFromStudentList, reportDate] = "x"

                    # Remove the attended student from the non-valid meeting attendance report data frame
                    self.__nonValidAR[reportDate] = self.__nonValidAR[reportDate].drop(studentFromMeetingReport)

                # If the similarity between names is >= 85 then the student is considered attended
                elif similarityMatrix.loc[studentFromMeetingReport, studentFromStudentList] >= 85:
                    # Assign attended for the student in that date
                    self.__attendanceSheet.loc[studentFromStudentList, reportDate] = "x"

                    # Remove the attended student from the non-valid meeting attendance report data frame
                    self.__nonValidAR[reportDate] = self.__nonValidAR[reportDate].drop(studentFromMeetingReport)


    # Overriding the take participation method
    def takeParticipation(self):

        # nonValidPR is a dictionary that contains non-valid participation reports entries
        self.__nonValidPR = {}

        # Creating a dataframe for saving participation results
        self.__participationSheet = pd.DataFrame()
        self.__participationSheet["Student ID"] = self.__studentList["Student Id"]
        self.__participationSheet["Student Name"] = self.__studentList['Student Name']

        # get the course code
        courseCode = getCourseCode(self.__studentListPath)

        # List to store all files names
        fileList = []

        # Get all meeting attendance reports files
        for root, dirs, files in os.walk(self.__participationReportsPath):
            for file in files:
                # Check whether the file corresponds to the course specified
                if file.find(courseCode) != -1:
                    fileList.append(f"{self.__participationReportsPath}/{file}")

        # Iterating through all participation reports files
        for participationReport in fileList:

            # Get the report date
            reportDate = getReportDate(participationReport)

            # Initialize non-valid dictionary
            self.__nonValidPR[reportDate] = []

            # Initialize the participation for all students by zero
            self.__participationSheet[reportDate] = 0

            # Convert into numeric
            self.__participationSheet[reportDate] = self.__participationSheet[reportDate].apply(pd.to_numeric)

            # Open participation report file
            reportFile = open(participationReport, encoding="utf8")

            # To store times of first and last participation
            firstParticipationTime = None
            lastParticipationTime = None

            # Getting the first and last participation times
            for line in reportFile:
                if re.search("From .* to .* :", line):
                    participationList = re.split("(.*) From (.*) to", line)
                    time = participationList[1]
                    if firstParticipationTime is None:
                        firstParticipationTime = time
                    lastParticipationTime = time


            # calculating the time window where the participation counts

            # Lower side from the time window
            hours = int(firstParticipationTime.split(":")[0])
            minutes = int(firstParticipationTime.split(":")[1])
            seconds = int(firstParticipationTime.split(":")[2])
            participationLowWindow = datetime(1, 1, 1, hours, minutes, seconds) + timedelta(minutes = self.__dropFirst)

            # upper side from the time window
            hours = int(lastParticipationTime.split(":")[0])
            minutes = int(lastParticipationTime.split(":")[1])
            seconds = int(lastParticipationTime.split(":")[2])
            participationUpperWindow = datetime(1, 1, 1, hours, minutes, seconds) - timedelta(minutes = self.__dropLast)

            participationLowWindow = participationLowWindow.strftime("%H:%M:%S")
            participationUpperWindow = participationUpperWindow.strftime("%H:%M:%S")

            # Reset the file
            reportFile.seek(0, 0)

            for line in reportFile:
                # Check if line is a participation
                if re.search("From .* to .* :", line):
                    # Storing the time and student name for each participation
                    participationList = re.split("(.*) From (.*) to", line)
                    time = participationList[1]
                    studentName = removeNumbers(removeNonAlphanumeric(participationList[2]))
                    studentId = extractNumbers(participationList[2])

                    # Pass from the participation if it is not within the time window
                    if time <= participationLowWindow:
                        continue
                    if time >= participationUpperWindow:
                        continue


                    # Finding similarity between name in participation post and in student list
                    similarityMatrix = pd.DataFrame(index = self.__studentList.index)
                    similarityMatrix[studentName] = 0
                    similarityMatrix[studentName] = similarityMatrix[studentName].apply(pd.to_numeric)
                    for studentInList in similarityMatrix.index:
                        similarityMatrix.loc[studentInList, studentName] = fuzz.ratio(studentInList.lower(), studentName.lower())

                    # Finding student from the student list with maximum similarity
                    maxSimilarity = similarityMatrix.idxmax()[0]

                    # Check if the similarity is reasonable
                    if similarityMatrix.loc[maxSimilarity, studentName] >= 60 and\
                    fuzz.ratio(studentId, self.__studentList.loc[maxSimilarity, "Student Id"]) == 100:
                        # Increment the participation for that student
                        self.__participationSheet.loc[maxSimilarity, reportDate] = self.__participationSheet.loc[maxSimilarity, reportDate] + 1

                    elif similarityMatrix.loc[maxSimilarity, studentName] >= 85:
                        # Increment the participation for that student
                        self.__participationSheet.loc[maxSimilarity, reportDate] = self.__participationSheet.loc[maxSimilarity, reportDate] + 1

                    # If the similarity is not reasonable then the report is non-valid
                    else:
                        self.__nonValidPR[reportDate].append(line)

    # Method to output all participation results
    def saveResults(self):

        # get the course code
        courseCode = getCourseCode(self.__studentListPath)

        # Saving attendance results
        # The path of attendance sheet report
        attendanceSheetReportPath = f"{self.__outputPath}/{courseCode}-AttendanceSheet.csv"

        # Save attendance sheet report to the output folder
        self.__attendanceSheet.to_csv(attendanceSheetReportPath, index=False)

        # Iterating through all nonValidAR reports
        for reportDate in self.__nonValidAR:
            # The path of each non-valid report file
            nonValidReportPath = f"{self.__outputPath}/{courseCode}-{reportDate}-AR-NV.csv"
            # Change non-valid report columns order
            self.__nonValidAR[reportDate] = self.__nonValidAR[reportDate][["Name (Original Name)", "Duration"]]

            # Save non-valid reports to the output folder
            self.__nonValidAR[reportDate].to_csv(nonValidReportPath, index=False)


        # Saving participation results
        # The path of participation sheet report
        participationSheetReportPath = f"{self.__outputPath}/{courseCode}-ParticipationSheet.csv"

        # Save attendance sheet report to the output folder
        self.__participationSheet.to_csv(participationSheetReportPath, index=False)

        # Iterating through all nonValidAR reports
        for reportDate in self.__nonValidPR:
            # The path of each non-valid report file
            nonValidReportPath = f"{self.__outputPath}/{courseCode}-{reportDate}-PR-NV.txt"

            nonValidFile = open(nonValidReportPath, "w", encoding="utf-8")
            for nonValidParticipation in self.__nonValidPR[reportDate]:
                nonValidFile.write(f"{nonValidParticipation}\n")
