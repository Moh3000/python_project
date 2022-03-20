# Pandas used as dataframe to manipulate the files efficiently
import pandas as pd

# OptionParser to take options from user
from optparse import OptionParser

# Using some functions from sikit-learn to calculate cosine similarity between strings
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer

from fuzzywuzzy import fuzz

# Creating instance of option parser
from AttendanceTaker import AttendanceTaker

parser = OptionParser()

# -----------------------------
# Specifying the script options
# -----------------------------

# Student list sheet option
parser.add_option("--SL", "--studentListSheet", dest="studentListPath",
                  help="The path to the file that contains students list sheet")

# Meetings attendance reports option
parser.add_option("--AR", "--attendanceReports", dest="attendnaceReportsPath",
                  help="The path to the folder that contains the meetings attendance reports")

# Meetings participation reports option
parser.add_option("--PR", "--participationReports", dest="participationReportsPath",
                  help="The path to the folder that contains the meetings particiapation reports")

# Output path option
parser.add_option("--O", "--out", dest="outputPath",
                  help="The path to the folder that script results will be stored in")

# P: Minimum attendance duration to consider student as attended
parser.add_option("--P", dest="minimumDuration",
                  help="The minimum amount of minutes to consider a student as attended", type="int")
# Tb: The duration of time at the  that participation will not be considered
parser.add_option("--Tb", dest="dropFirst",
                  help="The duration of time at the beginning of the session that participation of students will not be considered", type="int")

# Te: The duration of time at the end of the session that participation will not be considered
parser.add_option("--Te", dest="dropLast",
                  help="The duration of time at the end of the session that participation of students will not be considered", type="int")

(options, args) = parser.parse_args()

print(options)

# Saving entered options in a variables
studentListPath = options.studentListPath
attendnaceReportsPath = options.attendnaceReportsPath
participationReportsPath = options.participationReportsPath
outputPath = options.outputPath
minimumDuration = options.minimumDuration
dropFirst = options.dropFirst
dropLast = options.dropLast

# Creating instance from attendance taker class, then run the functionality
attendanceTaker = AttendanceTaker(studentListPath, attendnaceReportsPath, participationReportsPath, outputPath, minimumDuration, dropFirst, dropLast)
attendanceTaker.loadStudents()
attendanceTaker.takeAttendance()
attendanceTaker.takeParticipation()
attendanceTaker.saveResults()