# Creating a module that contains all methods used in filtering and processing strings
import re

# Function to remove non-alphanumeric characters
def removeNonAlphanumeric(string):
    return re.sub(r'[^a-zA-Z0-9 ]', '', string).strip()

def extractNumbers(string):
    return re.sub(r'[^0-9]', '', string).strip()

def removeNumbers(string):
    return re.sub(r'[0-9]', '', string).strip()

def getCourseCode(studentListPath):
    return studentListPath.split("-")[0]

def getReportDate(attendanceReport):
    return re.split(f"[0-9]-(.*)-.*\.((csv)|(txt))$", attendanceReport)[1]