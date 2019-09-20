##### Edited by mjd119
###
### Importing things that are part of the standard google cloud package
###
import os
import sys
import logging #logging events for error detection
import random #random number generation
import webapp2 #the application framework
import json
import csv
import numpy #can only use version 1.6.1, not later
#http://numpy-discussion.10968.n7.nabble.com/ImportError-Importing-the-multiarray-numpy-extension-module-failed-td43935.html
#https://cloud.google.com/appengine/docs/standard/python/tools/built-in-libraries-27
import ssl
#The Databases
from google.appengine.ext import ndb #the new datastore
from google.appengine.ext import db  #the old datastore
#The Webapp framework
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
# These are used for connecting with external websites, such as our Mturk Verify site
import urllib
from google.appengine.api import urlfetch


###
### Importing third party packages in lib folder
### the official way to import third party packages from lib does not seem to work
### https://cloud.google.com/appengine/docs/standard/python/tools/using-libraries-python-27
### so instead I found another version that works at least on the development Servers
### https://stackoverflow.com/questions/14850853/how-to-include-third-party-python-libraries-in-google-app-engine
sys.path.insert(0, 'lib')
# Connecting to Mturk servers https://github.com/boto/boto
import boto #
from boto.mturk.connection import MTurkConnection
from boto.mturk.price import Price
# sessions / cookie library https://github.com/dound/gae-sessions
from gaesessions import get_current_session
#how to import your own python code, inside lib folder
import testimport
# TODO fix Twilio syntax (maybe only valid with certain version?)
# from twilio.rest import Client
import datetime
import time


# doRender is a function from Charles Severance's book Using Google App engine
# It renders the page and also adds the _base.htm templates
# When updating to Python 2.7, one line had to be updated:
# http://stackoverflow.com/questions/16004135/python-gae-assert-typedata-is-stringtype-write-argument-must-be-string
def doRender(handler, tname = 'index.htm', values = { }):
  temp = os.path.join(
      os.path.dirname(__file__),
      'templates/' + tname)
  if not os.path.isfile(temp):
    return False
  # Make a copy of the dictionary and add the path and session
  newval = dict(values)
  newval['path'] = handler.request.path
  handler.session = get_current_session()
  if 'username' and 'UserFirstName' in handler.session: # Checks that both are in the session
     newval['username'] = handler.session['username']
     newval['UserFirstName'] = handler.session['UserFirstName']

  outstr = template.render(temp, newval)
  handler.response.out.write(unicode(outstr))  #### This line was updated
  return True
#### Above is from book: Don't Touch! ####




###
### Data Models
###
# Used to put user reports in the database
class DataReport(ndb.Model):
    MinimumUTCTime = ndb.DateTimeProperty() # Minimum time and date required to give a report for a certain time of day
    TimezoneOffset = ndb.IntegerProperty() # Difference in minutes between user's local timezone and UTC (positive if UTC is ahead and negative if UTC is behind)
    created = ndb.DateTimeProperty(auto_now_add=True) # Exact time (UTC) when report was generated irrespective of the "time of day"
    usernum = ndb.IntegerProperty()
    username = ndb.StringProperty() # User's email they use to enter in each time they log in
    # Day = ndb.IntegerProperty() # Holds the day the user entered the data (Maximum of 4 data points per day: Night, Morning, Afternoon, Evening)

    timeOfDayInt = ndb.IntegerProperty() # Holds integer representing the time of day for when data point was reported (Night=0, Morning=1, Afternoon=2, Evening=3)
    timeOfDayString = ndb.StringProperty()
    IndependentVariableReportData = ndb.FloatProperty() # Holds data point for the Independent Variable
    DependentVariableReportData = ndb.FloatProperty() # Holds data point for the Dependent Variable
    ThirdVariableReportData = ndb.FloatProperty() # Holds data point for the Third Variable / Alternative Cause 1
    FourthVariableReportData = ndb.FloatProperty() # Holds data point for the Fourth Variable / Alternative Cause 2 (optional)
    FifthVariableReportData = ndb.FloatProperty() # Holds data point for the Fifth Variable / Alternative Cause 3 (optional)
class User(ndb.Model):
    #Created on user_create, UserCreateHandler
    MturkID = ndb.StringProperty()
    usernum = ndb.IntegerProperty()
    username = ndb.StringProperty() # User's email they use to enter in each time they log in
    condition = ndb.IntegerProperty() #assigned at user creation
    RandomNumbersChosenAtUserCreate = ndb.IntegerProperty(repeated=True)
    TrialNumberStoredInDatastore = ndb.IntegerProperty(default=1)
    # AjaxTrackProgress = ndb.IntegerProperty(default=0)
    created = ndb.DateTimeProperty(auto_now_add=True) #time when first created
    #Demographics page
    age = ndb.IntegerProperty()
    sex = ndb.IntegerProperty()
    ethnicity = ndb.IntegerProperty()
    race = ndb.IntegerProperty()
    # A feature for MTurk that is coming
    completion_code = ndb.IntegerProperty()
    # Created by Matthew Dodson
    UserFirstName = ndb.StringProperty()
    UserLastName = ndb.StringProperty()
    UserPhoneNumber = ndb.StringProperty() # Parsed later
    UserPeoplesoftID = ndb.StringProperty()
    UserDay = ndb.IntegerProperty(default=1) # Keeps track of what day the user is on (trial)
    ResearchQuestion = ndb.StringProperty()
    IndependentVariable = ndb.StringProperty()
    DependentVariable = ndb.StringProperty()
    ThirdVariable = ndb.StringProperty()
    FourthVariable = ndb.StringProperty() # Optional
    FifthVariable = ndb.StringProperty() # Optional
    IndependentVariableType = ndb.StringProperty() # Binary, categorical, continuous, discrete, ordinal # TODO how to set user-specified scale
    DependentVariableType = ndb.StringProperty()
    ThirdVariableType = ndb.StringProperty()
    FourthVariableType = ndb.StringProperty()
    FifthVariableType = ndb.StringProperty()
    IndependentVariableScaleMinimum = ndb.StringProperty()
    IndependentVariableScaleMaximum = ndb.StringProperty()
    DependentVariableScaleMinimum = ndb.StringProperty()
    DependentVariableScaleMaximum = ndb.StringProperty()
    ThirdVariableScaleMinimum = ndb.StringProperty()
    ThirdVariableScaleMaximum = ndb.StringProperty()
    FourthVariableScaleMinimum = ndb.StringProperty()
    FourthVariableScaleMaximum = ndb.StringProperty()
    FifthVariableScaleMinimum = ndb.StringProperty()
    FifthVariableScaleMaximum = ndb.StringProperty()
    IndependentVariableBinary1 = ndb.StringProperty()
    IndependentVariableBinary2 = ndb.StringProperty()
    DependentVariableBinary1 = ndb.StringProperty()
    DependentVariableBinary2 = ndb.StringProperty()
    ThirdVariableBinary1 = ndb.StringProperty()
    ThirdVariableBinary2 = ndb.StringProperty()
    FourthVariableBinary1 = ndb.StringProperty()
    FourthVariableBinary2 = ndb.StringProperty()
    FifthVariableBinary1 = ndb.StringProperty()
    FifthVariableBinary2 = ndb.StringProperty()
    IndependentVariableUnits = ndb.StringProperty()
    DependentVariableUnits = ndb.StringProperty()
    ThirdVariableUnits = ndb.StringProperty()
    FourthVariableUnits = ndb.StringProperty()
    FifthVariableUnits = ndb.StringProperty()
    PostStudyData = ndb.StringProperty(repeated=True)
    # Fix properties

class MeanTaskData(ndb.Model):
    usernum = ndb.IntegerProperty()
    username = ndb.StringProperty()
    tennumbers = ndb.IntegerProperty(repeated=True) #these are the ten numbers that subjects saw to judge the mean
    mean = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now=True)

# This is used in the PrgerAcrossPagesRecord Handlers
# It simply records which pages were loaded and when
class PageLoadTracker(ndb.Model):
    usernum = ndb.IntegerProperty()
    username = ndb.StringProperty()
    page = ndb.IntegerProperty()
    created = ndb.DateTimeProperty(auto_now=True)


# The NumOfUsers counter assigns each participant a unique integer. It currently uses the old datastore (db instead of ndb). See github issue for more details
class NumOfUsers(db.Model):
  counter = db.IntegerProperty(default=0)
@db.transactional
def create_or_increment_NumOfUsers():
  obj = NumOfUsers.get_by_key_name('NumOfUsers', read_policy=db.STRONG_CONSISTENCY)
  if not obj:
    obj = NumOfUsers(key_name='NumOfUsers')
  obj.counter += 1
  x=obj.counter
  obj.put()
  return(x)



###
### Handlers
###







###
### Debugging
###

class LoggingHandler(webapp.RequestHandler):
    def get(self):
        #We inserted a bunch of hashtags below because it can sometimes be hard to find python logs in the masses of text
        logging.info('############################################ This is a log sent to the python console - you can write whatever you want here! ############################################')
        doRender(self, 'logging.htm')






###
### User Handlers
###

class UserCreateHandler(webapp.RequestHandler):
  def get(self):
    self.session=get_current_session()
    doRender(
        self,
        'user_create.htm')
  def post(self):
    username = self.request.get('username').lower()
    UserFirstName = str(self.request.get('UserFirstName'))
    UserLastName = str(self.request.get('UserLastName'))
    UserPeoplesoftID = str(self.request.get('UserPeoplesoftID'))
    UserPhoneNumber = str(self.request.get('UserPhoneNumber'))
    UserNum = create_or_increment_NumOfUsers()
    RandomNumbersChosenAtUserCreate=[]
    if (UserNum%2==0):
        condition = 30 #mean = 30
    if (UserNum%2==1):
        condition = 50 #mean = 50

    for i in range(10):
        RandomNumbersChosenAtUserCreate.append(int(random.gauss(condition, 10)))
    newuser = User(RandomNumbersChosenAtUserCreate=RandomNumbersChosenAtUserCreate, username=username, usernum = UserNum,
    UserFirstName=UserFirstName, UserLastName=UserLastName, UserPhoneNumber=UserPhoneNumber, UserPeoplesoftID=UserPeoplesoftID,
    condition=condition)
    userkey = newuser.put()

    self.session=get_current_session()
    self.session['usernum']    = UserNum
    self.session['username']      = username
    self.session['UserFirstName'] = UserFirstName
    self.session['UserPeoplesoftID'] = UserPeoplesoftID
    self.session['userkey'] = userkey
    self.session['RandomNumbersChosenAtUserCreate'] = RandomNumbersChosenAtUserCreate
    self.session['condition'] = condition
    self.session['Page'] = 1 #this is for  order_across_pages
    self.session['TrialInCookie'] = 0
    return webapp2.redirect('/home')
class UserVerifyLoggedInHandler(webapp.RequestHandler):
  def get(self):
    self.session=get_current_session()
    if self.session.is_active():
    	logging.info("Yes logged in!")
    	doRender(self, 'user_verify_logged_in_success.htm')
        # Could also use a redirect here if need to run a handler; put the handler name in XXXX
    	# return webapp2.redirect('/XXXX')
    else:
    	logging.info("No, not logged in!")
    	doRender(self, 'login.htm')

class LoginHandler(webapp.RequestHandler):
  def get(self):
    self.session=get_current_session()
    if self.session.is_active():
        doRender(self, 'user_verify_logged_in_success.htm')
    else:
    	doRender(self, 'login.htm')

  def post(self):
    username=self.request.get('username').lower()
    UserQue=User.query(User.username == username)
    results=UserQue.fetch(1)
    #technically, results is a list, and the only element is the user object

    if (len(results) == 0):
    	self.response.out.write("There is no user with this username.")
    else:
        # This stores all the critical data in the session
    	self.session=get_current_session()
        self.session['UserPeoplesoftID'] = results[0].UserPeoplesoftID
    	self.session['username']  = results[0].username
        self.session['UserFirstName'] = results[0].UserFirstName
    	self.session['userkey']   = results[0].key
    	self.session['usernum']   = results[0].usernum
    	self.session['condition'] = results[0].condition
    	self.session['Page']      = results[0].condition
        self.session['TrialInCookie'] = 0
        return webapp2.redirect('/login')
class LogoutHandler(webapp.RequestHandler):
  def get(self):
    self.session = get_current_session()
    self.session.terminate() #removes the cookie/session
    doRender(self,'logout.htm')


###
### Condition Randomization and Stimuli Presentation
###

class StimuliPresentationHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            condition = self.session['condition']
            logging.info("condition")
            logging.info(condition)

    # 		Random 1 Version in which stimuli is obtained from a csv file
    #		In the CSV file, the first 10 data points are for a M=37, SD=10 distribution. The next 10 are for a M=65, SD=10 distribution. The code below shows how to import the data and subset it.
            f = open('stimuli/RandomNumbersFromCSV.csv', 'rU')
            mycsv = csv.reader(f)
            mycsv = numpy.array(list(mycsv))
            mycsv=numpy.loadtxt(open("stimuli/RandomNumbersFromCSV.csv","rU"),delimiter=",",skiprows=1)
            if condition == 30: #the condition with mean=30
                RandomNumbersFromCSV = mycsv[0:10,2] #This uses numpy slicing to get the first 10 rows of the third column
            elif condition == 50:
                RandomNumbersFromCSV = mycsv[10:20,2]
            RandomNumbersFromCSV = list(RandomNumbersFromCSV)
            RandomNumbersFromCSV = [int(i) for i in RandomNumbersFromCSV]

    #		Random 2 Version in which the stimuli were created at the time that the user was initialized on create_user.
    #		There are two ways to pull the already-created data. The first is through the cookie (session).
    #		The second is by accessing the data from the datastore. The datastore requires more code, and is more costly because it involves a query of the datastore.
    # 		RandomNumbersChosenAtUserCreate = self.session['RandomNumbersChosenAtUserCreate']
    # 		or
            results = self.session['userkey'].get()
            RandomNumbersChosenAtUserCreate = results.RandomNumbersChosenAtUserCreate
    		# when RandomNumbersChosenAtUserCreate is stored, it is stored with "L" after each item which is a Python way to represent that each item is a Long type. This needs to be converted to an integer.
            RandomNumbersChosenAtUserCreate = [int(i) for i in RandomNumbersChosenAtUserCreate]

    # 		Rand3 Version in which stimuli is made in the 'back end' by the server and sent to the browser
    # 		In this version, a new set of data is calculated each time the page loads. If you want each user to have a pre-specified set of data. Set the data at the time of the user, and call it from the database or the cookie.
            RandomNumbersCreatedByPythonOnPageLoad=[]
            for i in range(10):
                RandomNumbersCreatedByPythonOnPageLoad.append(int(random.gauss(condition, 10)))
    # 		Random4 Version in which stimuli is made in the browser using javascript
    # 		In this case, nothing needs to be sent to the browser.


            doRender(self, 'stimuli_presentation.htm', {'RandomNumbersFromCSV': RandomNumbersFromCSV, 'RandomNumbersChosenAtUserCreate': RandomNumbersChosenAtUserCreate, 'RandomNumbersCreatedByPythonOnPageLoad': RandomNumbersCreatedByPythonOnPageLoad, 'condition': condition})









###
### Saving Data to the Datastore
###

class SavingDataPostHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            condition = self.session['condition']
            logging.info("condition")
            logging.info(condition)

    # 		Random 1 Version in which stimuli is obtained from a csv file
    #		In the CSV file, the first 10 data points are for a M=37, SD=10 distribution. The next 10 are for a M=65, SD=10 distribution. The code below shows how to import the data and subset it.
            f = open('stimuli/RandomNumbersFromCSV.csv', 'rU')
            mycsv = csv.reader(f)
            mycsv = numpy.array(list(mycsv))
            mycsv=numpy.loadtxt(open("stimuli/RandomNumbersFromCSV.csv","rU"),delimiter=",",skiprows=1)
            if condition == 30: #the condition with mean=30
                RandomNumbersFromCSV = mycsv[0:10,2] #This uses numpy slicing to get the first 10 rows of the third column
            elif condition == 50:
                RandomNumbersFromCSV = mycsv[10:20,2]
            RandomNumbersFromCSV = list(RandomNumbersFromCSV)
            RandomNumbersFromCSV = [int(i) for i in RandomNumbersFromCSV]

            doRender(self, 'saving_data_post.htm', {'RandomNumbersFromCSV': RandomNumbersFromCSV, 'condition': condition})

    def post(self):
        self.session=get_current_session()
        tennumbers=self.request.get('tennumbers')
        logging.info(tennumbers)
        tennumbers=map(int,tennumbers.split(","))
        mean=self.request.get('Mean')
        newinput = MeanTaskData()
        newinput.usernum        =self.session['usernum']
        newinput.username        =self.session['username']
        newinput.tennumbers     =tennumbers
        newinput.mean           =mean
        newinput.put();
        return webapp2.redirect('/saving_data_post_success')

class SavingDataPostSuccessHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        doRender(self, 'saving_data_post_success.htm', {})

class SavingDataAjaxHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            condition = self.session['condition']
            logging.info("condition")
            logging.info(condition)

    # 		Random 1 Version in which stimuli is obtained from a csv file
    #		In the CSV file, the first 10 data points are for a M=37, SD=10 distribution. The next 10 are for a M=65, SD=10 distribution. The code below shows how to import the data and subset it.
            f = open('stimuli/RandomNumbersFromCSV.csv', 'rU')
            mycsv = csv.reader(f)
            mycsv = numpy.array(list(mycsv))
            mycsv=numpy.loadtxt(open("stimuli/RandomNumbersFromCSV.csv","rU"),delimiter=",",skiprows=1)
            if condition == 30: #the condition with mean=30
                RandomNumbersFromCSV = mycsv[0:10,2] #This uses numpy slicing to get the first 10 rows of the third column
            elif condition == 50:
                RandomNumbersFromCSV = mycsv[10:20,2]
            RandomNumbersFromCSV = list(RandomNumbersFromCSV)
            RandomNumbersFromCSV = [int(i) for i in RandomNumbersFromCSV]

            doRender(self, 'saving_data_ajax.htm', {'RandomNumbersFromCSV': RandomNumbersFromCSV, 'condition': condition})

    def post(self):
        self.session=get_current_session()
        tennumbers=self.request.get('tennumbers')
        tennumbers=map(int,tennumbers.split(","))
        mean=int(self.request.get('Mean'))
        newinput = MeanTaskData()
        newinput.usernum        =self.session['usernum']
        newinput.username       =self.session['username']
        newinput.tennumbers     =tennumbers
        newinput.mean           =mean
        newinput.put();
        self.response.out.write(json.dumps(({'blah': 'blah'}))) #not sure why need this but without it get an error









###
### Seeing and Downloading Data
###
class DownloadingDataHandler(webapp.RequestHandler):
  def get(self):
    self.session=get_current_session()
    if not self.session.is_active():
        doRender(self, 'login.htm')
    else:
        doRender(self,'downloading_data_login.htm',{})

  def post(self):
    password=self.request.get('password')
    if password == "MyPassword": #If the password is correct
        self.session=get_current_session()

        # these queries filter the data such that only the logged-in user gets included. To include all participants, remove the "MeanTaskData.usernum == self.session['usernum']"

        MeansTaskDataQue=MeanTaskData.query(MeanTaskData.username == self.session['username'])
        MeansTaskDataQue=MeansTaskDataQue.order(MeanTaskData.usernum).order(MeanTaskData.created)
        MTD=MeansTaskDataQue.fetch(10)

        # This code below is for converting the data to long format.
        usernum=[]
        username=[]
        mean=[]
        Order=[]
        tennumbers=[]
        for x in range (0, len(MTD)):
            usernum = usernum + [MTD[x].usernum] * 10
            username = username + [MTD[x].username] * 10
            mean = mean + [MTD[x].mean] * 10
            Order = Order + range(1,11)
            tennumbers = tennumbers + MTD[x].tennumbers
        MTDLong = zip(usernum, username, mean, Order, tennumbers)
        # Note, these columns are not named

        UserQue=User.query(User.usernum == self.session['usernum'])
        UserQue=UserQue.order(User.usernum)
        UserData=UserQue.fetch(100)

        PageQue=PageLoadTracker.query(PageLoadTracker.usernum == self.session['usernum'])
        PageQue = PageQue.order(PageLoadTracker.created)
        PageData=PageQue.fetch(1000)

        doRender(self, 'downloading_data.htm', {'MTD': MTD, 'MTDLong': MTDLong, 'User': UserData, 'PageData': PageData})
    else: # If the password is incorrect
        doRender(self,'downloading_data_login_fail.htm',{})











###
### Linking with Mturk :: This code is old and has not been updated !!!!!
###


class MturkIDHandler(webapp.RequestHandler):
  def get(self):
    self.session=get_current_session()
    if not self.session.is_active():
        doRender(self, 'login.htm')
    else:
        doRender(self, 'mturkid.htm')

  def post(self):
    ID=self.request.get('ID')
    acct=ID

    form_fields = {
      "ID": ID,
      "ClassOfStudies": 1,
      "StudyNumber": 4
      }
    form_data = urllib.urlencode(form_fields)
    url="http://www.mturk-qualify.appspot.com"
    result = urlfetch.fetch(url=url,
                            payload=form_data,
                            method=urlfetch.POST,
                            headers={'Content-Type': 'application/x-www-form-urlencoded'})

    if result.content=="0":
      #self.response.out.write("ID is in global database.")
      doRender(self, 'do_not_qualify.htm')

    elif result.content=="1":


    # Check if the user already exists


      results = User.query(MturkID == ID).fetch(1)

      if (len(results) > 0) & (ID!='ben'):   #allows username 'ben' to pass
        #self.response.out.write("ID is in local database.")
        doRender(self, 'do_not_qualify.htm')

      else:
		######### Create the User object and log the user in ############
		## if user does not exist
		self.session=get_current_session()

		UserNum    = create_or_increment_NumOfUsers()



		CoverStory = UserNum%2

		Autocorrel = [1,0]
		TSDC = [0,0]
		data = timeseries(Autocorrel[CoverStory])
		LeftRight = random.randint(0,1)
		logging.info(LeftRight)
		newuser = User(MturkID=acct, usernum=UserNum, data=data, LeftRight=LeftRight, CoverStory=CoverStory, Autocorrel=Autocorrel[CoverStory], TSDC=TSDC[CoverStory]);
		pkey = newuser.put()
# 		newuser.put() I think that this is redundant to the thing above


		self.session['usernum']    = UserNum
		self.session['username']   = acct
		self.session['userkey']    = pkey
		self.session['scenario']   = CoverStory
		self.session['data']       = data
		self.session['LeftRight']  = LeftRight
		self.session['UserNum']    = UserNum
		self.session['BonusList']  = []
		self.session['CoverStory']  = CoverStory
		self.session['Autocorrel'] = Autocorrel[CoverStory]
		self.session['TSDC'] = TSDC[CoverStory]
		self.session['CurrentDay'] = 1
		self.session['Page'] = 1 #this is for  order_across_pages

		doRender(
            self,
            'initial2weeks.htm',
            {'CoverStory': self.session['CoverStory'],
            'timeseries': data[0:14],
            'LeftRight': self.session['LeftRight'],
            'LengthOfData': 14})

    else:
      error="The surver is going slowly. Please reload and try again."
      self.response.out.write(result.content)

class DNQHandler(webapp.RequestHandler):
  def get(self):
    doRender(self, 'do_not_qualify.htm')






###
### Ensuring that the order of the study is followed - tracking progress within a page
###


class TrackingProgressWithinAPageWithHTML5WebStorage(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            condition = self.session['condition']
            results = self.session['userkey'].get()
            trial_number = results.TrialNumberStoredInDatastore

            f = open('stimuli/RandomNumbersFromCSV.csv', 'rU')
            mycsv = csv.reader(f)
            mycsv = numpy.array(list(mycsv))
            mycsv=numpy.loadtxt(open("stimuli/RandomNumbersFromCSV.csv","rU"),delimiter=",",skiprows=1)

            if condition == 30: #the condition with mean=30
                RandomNumbersFromCSV = mycsv[0:10,2] #This uses numpy slicing to get the first 10 rows of the third column
            elif condition == 50:
                RandomNumbersFromCSV = mycsv[10:20,2]

            RandomNumbersFromCSV = list(RandomNumbersFromCSV)
            RandomNumbersFromCSV = [int(i) for i in RandomNumbersFromCSV]

            doRender(self, 'tracking_progress_within_a_page_with_HTML5_Web_Storage.htm', {'RandomNumbersFromCSV': RandomNumbersFromCSV, 'condition': condition, 'trial_number': trial_number})

    def post(self):
        self.session=get_current_session()
        u = self.session['userkey'].get()
        n = int(self.request.get('TrialNumberAjaxForm'))
        u.TrialNumberStoredInDatastore = n
        u.put()
        self.response.out.write(json.dumps(({'blah': 'blah'}))) #not sure why need this but without it get an error


class TrackingProgressWithinAPageWithAJAXAndSessions(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            condition = self.session['condition']
            results = self.session['userkey'].get()
            trial_number = results.TrialNumberStoredInDatastore

            f = open('stimuli/RandomNumbersFromCSV.csv', 'rU')
            mycsv = csv.reader(f)
            mycsv = numpy.array(list(mycsv))
            mycsv=numpy.loadtxt(open("stimuli/RandomNumbersFromCSV.csv","rU"),delimiter=",",skiprows=1)

            if condition == 30: #the condition with mean=30
                RandomNumbersFromCSV = mycsv[0:10,2] #This uses numpy slicing to get the first 10 rows of the third column
            elif condition == 50:
                RandomNumbersFromCSV = mycsv[10:20,2]

            RandomNumbersFromCSV = list(RandomNumbersFromCSV)
            RandomNumbersFromCSV = [int(i) for i in RandomNumbersFromCSV]

            doRender(self, 'tracking_progress_within_a_page_with_AJAX_and_sessions.htm', {'RandomNumbersFromCSV': RandomNumbersFromCSV, 'condition': condition, 'trial_number': trial_number})

    def post(self):
        self.session=get_current_session()
        u = self.session['userkey'].get()
        n = int(self.request.get('TrialNumberAjaxForm'))
        u.TrialNumberStoredInDatastore = n
        u.put()
        self.response.out.write(json.dumps(({'blah': 'blah'}))) #not sure why need this but without it get an error



class TrackingProgressWithinAPageWithAJAXAndTheDatastore(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            condition = self.session['condition']
            results = self.session['userkey'].get()
            trial_number = results.TrialNumberStoredInDatastore

            f = open('stimuli/RandomNumbersFromCSV.csv', 'rU')
            mycsv = csv.reader(f)
            mycsv = numpy.array(list(mycsv))
            mycsv=numpy.loadtxt(open("stimuli/RandomNumbersFromCSV.csv","rU"),delimiter=",",skiprows=1)

            if condition == 30: #the condition with mean=30
                RandomNumbersFromCSV = mycsv[0:10,2] #This uses numpy slicing to get the first 10 rows of the third column
            elif condition == 50:
                RandomNumbersFromCSV = mycsv[10:20,2]

            RandomNumbersFromCSV = list(RandomNumbersFromCSV)
            RandomNumbersFromCSV = [int(i) for i in RandomNumbersFromCSV]

            doRender(self, 'tracking_progress_within_a_page_with_AJAX_and_the_datastore.htm', {'RandomNumbersFromCSV': RandomNumbersFromCSV, 'condition': condition, 'trial_number': trial_number})

    def post(self):
        self.session=get_current_session()
        u = self.session['userkey'].get()
        n = int(self.request.get('TrialNumberAjaxForm'))
        u.TrialNumberStoredInDatastore = n
        u.put()
        self.response.out.write(json.dumps(({'blah': 'blah'}))) #not sure why need this but without it get an error

###
### Ensuring that the order of the study is followed - tracking progress across pages
###

class RecordingEachPageLoadPage1Handler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            newinput = PageLoadTracker()
            newinput.usernum=self.session['usernum']
            newinput.username=self.session['username']
            newinput.page=1
            newinput.put();

            # self.response.pragma = 'Public'
            # https://blog.55minutes.com/2011/10/how-to-defeat-the-browser-back-button-cache/
            self.response.cache_expires(0)
            self.response.headers.add("Cache-Control", "no-store")
            self.response.headers.add("Cache-Control", "max-age=0")
            doRender(self, 'recording_each_page_load_page_1.htm', {})

class RecordingEachPageLoadPage2Handler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            newinput = PageLoadTracker()
            newinput.usernum=self.session['usernum']
            newinput.username=self.session['username']
            newinput.page=2
            newinput.put();

            # self.response.pragma = 'Public'
            # https://blog.55minutes.com/2011/10/how-to-defeat-the-browser-back-button-cache/
            self.response.cache_expires(0)
            self.response.headers.add("Cache-Control", "no-store")
            self.response.headers.add("Cache-Control", "max-age=0")
            doRender(self, 'recording_each_page_load_page_2.htm', {})

class RecordingEachPageLoadPage3Handler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            newinput = PageLoadTracker()
            newinput.usernum=self.session['usernum']
            newinput.username=self.session['username']
            newinput.page=3
            newinput.put();

            # self.response.pragma = 'Public'
            # https://blog.55minutes.com/2011/10/how-to-defeat-the-browser-back-button-cache/
            self.response.cache_expires(0)
            self.response.headers.add("Cache-Control", "no-store")
            self.response.headers.add("Cache-Control", "max-age=0")
            doRender(self, 'recording_each_page_load_page_3.htm', {})

class UsingCookiesToKeepTheUserFromGoingBackHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            logging.info(self.session['userkey'])
            logging.info(self.session['Page'])
            Page = self.session['Page']
            if Page == 1:
                render='using_cookies_to_keep_the_user_from_going_back_page_1.htm'
            elif Page == 2:
                render='using_cookies_to_keep_the_user_from_going_back_page_2.htm'
            elif Page >= 3:
                render='using_cookies_to_keep_the_user_from_going_back_page_3.htm'

            # self.response.pragma = 'Public'
            # https://blog.55minutes.com/2011/10/how-to-defeat-the-browser-back-button-cache/
            self.response.cache_expires(0)
            self.response.headers.add("Cache-Control", "no-cache")
            self.response.headers.add("Cache-Control", "no-store")
            self.response.headers.add("Cache-Control", "max-age=0")
            self.response.headers.add("Cache-Control", "must-revalidate")

            doRender(self, render, {})

    def post(self):
        self.session=get_current_session()
        ToPage = int(self.request.get('ToPage'))
        if ToPage == 1:
            render='using_cookies_to_keep_the_user_from_going_back_page_1.htm'
            self.session['Page'] = 1
        elif ToPage == 2:
            render='using_cookies_to_keep_the_user_from_going_back_page_2.htm'
            self.session['Page'] = 2
        elif ToPage == 3:
            render='using_cookies_to_keep_the_user_from_going_back_page_3.htm'
            self.session['Page'] = 3

        self.response.cache_expires(0)
        self.response.headers.add("Cache-Control", "no-cache")
        self.response.headers.add("Cache-Control", "no-store")
        self.response.headers.add("Cache-Control", "no-max-age=0")
        self.response.headers.add("Cache-Control", "must-revalidate")
        doRender(self, render, {})











###
### Piping Text ... tbd
###






###
### Communicating with Mturk Servers
###

class BotoGetAccountBalanceHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            doRender(self, 'boto_get_account_balance_input.htm')
    def post(self):
        ACCESS_ID = self.request.get("AWSAccessKeyID")
        SECRET_KEY = self.request.get("AWSSecretAccessKey")

#Currently this host does not seem to allow switching between sandbox vs. live because of the edit to Connection.py
        HOST = 'mechanicalturk.amazonaws.com'
        # HOST = 'mechanicalturk.sandbox.amazonaws.com'

        mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,aws_secret_access_key=SECRET_KEY,host=HOST)
        AccountBalance = mtc.get_account_balance()[0]
        doRender(self, 'boto_get_account_balance.htm', {'AccountBalance': AccountBalance})

class BotoQueryingAHitHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            doRender(self, 'boto_querying_a_hit_input.htm')
    def post(self):
        ACCESS_ID = self.request.get("AWSAccessKeyID")
        SECRET_KEY = self.request.get("AWSSecretAccessKey")
        HIT_ID = self.request.get("HIT_ID")

# Currently this host does not seem to allow switching between sandbox vs. live because of the edit to Connection.py
        HOST = 'mechanicalturk.amazonaws.com'
        # HOST = 'mechanicalturk.sandbox.amazonaws.com'

        mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,aws_secret_access_key=SECRET_KEY,host=HOST)
        Hit = mtc.get_hit(hit_id = HIT_ID)[0]

        All_Assignments = mtc.get_assignments(hit_id=HIT_ID, )
        logging.info(All_Assignments)

        doRender(self, 'boto_querying_a_hit.htm', {'Hit': [Hit], 'All_Assignments': All_Assignments})






###
### Fixed Width
###

class NonResponsiveHandler(webapp.RequestHandler):
  def get(self):
    doRender(self,'nonresponsive.htm')


###
### Useful Resources
###
class DemographicsHandler(webapp.RequestHandler):
  def get(self):
    self.session=get_current_session()
    if not self.session.is_active():
        doRender(self, 'login.htm')
    else:
        doRender(self, 'demographics.htm')
  def post(self):
	self.session=get_current_session()

	age=int(self.request.get('age'))
	sex=int(self.request.get('sex'))
	ethnicity=int(self.request.get('ethnicity'))
	racel=map(int,self.request.get_all('race')) #race list
	logging.info("race list")
	logging.info(racel)

	rl1=int(1 in racel)
	rl2=int(2 in racel)
	rl3=int(3 in racel)
	rl4=int(4 in racel)
	rl5=int(5 in racel)
	rl6=int(6 in racel)
	rl7=int(7 in racel)

	#Amer Indian, Asian, Native Hawaiian, Black, White, More than one, No Report
	#race_num is a number corresponding to a single race Amer Indian (1) through White(5)
	race_num=rl1*1+rl2*2+rl3*3+rl4*4+rl5*5

	morethanonerace=0
	for i in [rl1,rl2,rl3,rl4,rl5]:
		if i==1:
			morethanonerace+=1
	if rl6==1:
		morethanonerace+=2

	if rl7==1:	#dont want to report
		race=7
	elif morethanonerace>1:
		race=6
	elif morethanonerace==1:
		race=race_num

	logging.info("race")
	logging.info(race)



	completion_code=random.randint(10000000,99999999)


	obj = self.session['userkey'].get()
	obj.age = age
	obj.sex = sex
	obj.ethnicity = ethnicity
	obj.race = race
	obj.put()

	return webapp2.redirect('/')
# Handler for the homepage the user first sees
class OverviewHandler(webapp.RequestHandler):
    def get(self):
        doRender(self, 'overview.htm')
class HomeHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            doRender(self, 'home.htm')
    def post(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            return webapp2.redirect('/questionivdv')
class QuestionIVDVHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            RQ = obj.ResearchQuestion
            IV = obj.IndependentVariable
            DV = obj.DependentVariable
            doRender(self, 'questionivdv.htm', {'RQ': RQ, 'IV': IV, 'DV': DV})
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        RQ = str(self.request.get('RQ'))
        IV = str(self.request.get('IV'))
        DV = str(self.request.get('DV'))
        obj.ResearchQuestion = RQ
        obj.IndependentVariable = IV
        obj.DependentVariable = DV
        obj.put()
        return webapp2.redirect('/selectvariabletype')
class SelectVariableTypeHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            RQ = obj.ResearchQuestion
            IV = obj.IndependentVariable
            DV = obj.DependentVariable
            IVType = obj.IndependentVariableType
            DVType = obj.DependentVariableType
            IVUnits = obj.IndependentVariableUnits
            DVUnits = obj.DependentVariableUnits
            IVScaleMin = obj.IndependentVariableScaleMinimum
            IVScaleMax = obj.IndependentVariableScaleMaximum
            DVScaleMin = obj.DependentVariableScaleMinimum
            DVScaleMax = obj.DependentVariableScaleMaximum
            IVBinary1 = obj.IndependentVariableBinary1
            IVBinary2 = obj.IndependentVariableBinary2
            DVBinary1 = obj.DependentVariableBinary1
            DVBinary2 = obj.DependentVariableBinary2
            doRender(self, 'selectvariabletype.htm', {'RQ': RQ, 'IV': IV, 'DV': DV,
            'IVType': IVType, 'DVType': DVType, 'IVUnits': IVUnits, 'DVUnits': DVUnits,
            'IVScaleMin': IVScaleMin, 'IVScaleMax': IVScaleMax, 'DVScaleMin': DVScaleMin,
            'DVScaleMax': DVScaleMax, 'IVBinary1': IVBinary1, 'IVBinary2': IVBinary2,
            'DVBinary1': DVBinary1, 'DVBinary2': DVBinary2})
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        IVType = str(self.request.get('IVType'))
        DVType = str(self.request.get('DVType'))
        IVUnits = str(self.request.get('IVUnits'))
        DVUnits = str(self.request.get('DVUnits'))
        IVScaleMin = str(self.request.get('IVScaleMin'))
        IVScaleMax = str(self.request.get('IVScaleMax'))
        DVScaleMin = str(self.request.get('DVScaleMin'))
        DVScaleMax = str(self.request.get('DVScaleMax'))
        IVBinary1 = str(self.request.get('IVBinary1'))
        IVBinary2 = str(self.request.get('IVBinary2'))
        DVBinary1 = str(self.request.get('DVBinary1'))
        DVBinary2 = str(self.request.get('DVBinary2'))
        obj.IndependentVariableType = IVType
        obj.DependentVariableType = DVType
        obj.IndependentVariableUnits = IVUnits
        obj.DependentVariableUnits = DVUnits
        obj.IndependentVariableScaleMinimum = IVScaleMin
        obj.IndependentVariableScaleMaximum = IVScaleMax
        obj.DependentVariableScaleMinimum = DVScaleMin
        obj.DependentVariableScaleMaximum = DVScaleMax
        obj.IndependentVariableBinary1 = IVBinary1
        obj.IndependentVariableBinary2 = IVBinary2
        obj.DependentVariableBinary1 = DVBinary1
        obj.DependentVariableBinary2 = DVBinary2
        obj.put()
        return webapp2.redirect('/chooseextravariables')
class ChooseExtraVariablesHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            RQ = obj.ResearchQuestion
            IV = obj.IndependentVariable
            DV = obj.DependentVariable
            var3 = obj.ThirdVariable
            var4 = obj.FourthVariable
            var5 = obj.FifthVariable
            IVType = obj.IndependentVariableType
            DVType = obj.DependentVariableType
            var3Type = obj.ThirdVariableType
            var4Type = obj.FourthVariableType
            var5Type = obj.FifthVariableType
            IVUnits = obj.IndependentVariableUnits
            DVUnits = obj.DependentVariableUnits
            var3Units = obj.ThirdVariableUnits
            var4Units = obj.FourthVariableUnits
            var5Units = obj.FifthVariableUnits
            IVScaleMin = obj.IndependentVariableScaleMinimum
            IVScaleMax = obj.IndependentVariableScaleMaximum
            DVScaleMin = obj.DependentVariableScaleMinimum
            DVScaleMax = obj.DependentVariableScaleMaximum
            var3ScaleMin = obj.ThirdVariableScaleMinimum
            var3ScaleMax = obj.ThirdVariableScaleMaximum
            var4ScaleMin = obj.FourthVariableScaleMinimum
            var4ScaleMax = obj.FourthVariableScaleMaximum
            var5ScaleMin = obj.FifthVariableScaleMinimum
            var5ScaleMax = obj.FifthVariableScaleMaximum
            IVBinary1 = obj.IndependentVariableBinary1
            IVBinary2 = obj.IndependentVariableBinary2
            DVBinary1 = obj.DependentVariableBinary1
            DVBinary2 = obj.DependentVariableBinary2
            var3Binary1 = obj.ThirdVariableBinary1
            var3Binary2 = obj.ThirdVariableBinary2
            var4Binary1 = obj.FourthVariableBinary1
            var4Binary2 = obj.FourthVariableBinary2
            var5Binary1 = obj.FifthVariableBinary1
            var5Binary2 = obj.FifthVariableBinary2
            doRender(self, 'chooseextravariables.htm', {'RQ': RQ, 'IV': IV, 'DV': DV, 'var3': var3, 'var4': var4, 'var5': var5,
            'IVType': IVType, 'DVType': DVType, 'var3Type': var3Type, 'var4Type': var4Type, 'var5Type': var5Type,
            'IVUnits': IVUnits, 'DVUnits': DVUnits, 'var3Units': var3Units, 'var4Units': var4Units, 'var5Units': var5Units,
            'IVScaleMin': IVScaleMin, 'IVScaleMax': IVScaleMax, 'DVScaleMin': DVScaleMin, 'var3ScaleMin': var3ScaleMin,
            'var3ScaleMax': var3ScaleMax, 'var4ScaleMin': var4ScaleMin, 'var4ScaleMax': var4ScaleMax, 'var5ScaleMin': var5ScaleMin,
            'var5ScaleMax': var5ScaleMax, 'DVScaleMax': DVScaleMax, 'IVBinary1': IVBinary1, 'IVBinary2': IVBinary2,
            'DVBinary1': DVBinary1, 'DVBinary2': DVBinary2, 'var3Binary1': var3Binary1, 'var3Binary2': var3Binary2,
            'var4Binary1': var4Binary1, 'var4Binary2': var4Binary2, 'var5Binary1': var5Binary1, 'var5Binary2': var5Binary2})
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        var3 = str(self.request.get('var3'))
        var4 = str(self.request.get('var4'))
        var5 = str(self.request.get('var5'))
        var3Type = str(self.request.get('var3Type'))
        var4Type = str(self.request.get('var4Type'))
        var5Type = str(self.request.get('var5Type'))
        var3Units = str(self.request.get('var3Units'))
        var4Units = str(self.request.get('var4Units'))
        var5Units = str(self.request.get('var5Units'))
        var3ScaleMin = str(self.request.get('var3ScaleMin'))
        var3ScaleMax = str(self.request.get('var3ScaleMax'))
        var4ScaleMin = str(self.request.get('var4ScaleMin'))
        var4ScaleMax = str(self.request.get('var4ScaleMax'))
        var5ScaleMin = str(self.request.get('var5ScaleMin'))
        var5ScaleMax = str(self.request.get('var5ScaleMax'))
        var3Binary1 = str(self.request.get('var3Binary1'))
        var3Binary2 = str(self.request.get('var3Binary2'))
        var4Binary1 = str(self.request.get('var4Binary1'))
        var4Binary2 = str(self.request.get('var4Binary2'))
        var5Binary1 = str(self.request.get('var5Binary1'))
        var5Binary2 = str(self.request.get('var5Binary2'))
        obj.ThirdVariable = var3
        obj.ThirdVariableType = var3Type
        obj.ThirdVariableUnits = var3Units
        obj.ThirdVariableScaleMinimum = var3ScaleMin
        obj.ThirdVariableScaleMaximum = var3ScaleMax
        obj.ThirdVariableBinary1 = var3Binary1
        obj.ThirdVariableBinary2 = var3Binary2
        obj.FourthVariable = var4
        obj.FourthVariableType = var4Type
        obj.FourthVariableUnits = var4Units
        obj.FourthVariableScaleMinimum = var4ScaleMin
        obj.FourthVariableScaleMaximum = var4ScaleMax
        obj.FourthVariableBinary1 = var4Binary1
        obj.FourthVariableBinary2 = var4Binary2
        obj.FifthVariable = var5
        obj.FifthVariableType = var5Type
        obj.FifthVariableUnits = var5Units
        obj.FifthVariableScaleMinimum = var5ScaleMin
        obj.FifthVariableScaleMaximum = var5ScaleMax
        obj.FifthVariableBinary1 = var5Binary1
        obj.FifthVariableBinary2 = var5Binary2
        obj.put()
        return webapp2.redirect('/designoverview')
class ChoooseDailyQuestionsHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            RQ = obj.ResearchQuestion
            IV = obj.IndependentVariable
            DV = obj.DependentVariable
            var3 = obj.ThirdVariable
            var4 = obj.FourthVariable
            var5 = obj.FifthVariable
            IVType = obj.IndependentVariableType
            DVType = obj.DependentVariableType
            var3Type = obj.ThirdVariableType
            var4Type = obj.FourthVariableType
            var5Type = obj.FifthVariableType
            IVUnits = obj.IndependentVariableUnits
            DVUnits = obj.DependentVariableUnits
            var3Units = obj.ThirdVariableUnits
            var4Units = obj.FourthVariableUnits
            var5Units = obj.FifthVariableUnits
            doRender(self, 'choosedailyquestions.htm', {'RQ': RQ, 'IV': IV, 'DV': DV, 'var3': var3, 'var4': var4, 'var5': var5,
            'IVType': IVType, 'DVType': DVType, 'var3Type': var3Type, 'var4Type': var4Type, 'var5Type': var5Type, 'IVUnits': IVUnits,
            'DVUnits': DVUnits, 'var3Units': var3Units, 'var4Units': var4Units, 'var5Units': var5Units})
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        IVQuestion = str(self.request.get('IVQuestion'))
        DVQuestion = str(self.request.get('DVQuestion'))
        var3Question = str(self.request.get('var3Question'))
        var4Question = str(self.request.get('var4Question'))
        var5Question = str(self.request.get('var5Question'))
        obj.IndependentVariableQuestion = IVQuestion
        obj.DependentVariableQuestion = DVQuestion
        obj.ThirdVariableQuestion = var3Question
        obj.FourthVariableQuestion = var4Question
        obj.FifthVariableQuestion = var5Question
        obj.put()
        return webapp2.redirect('/designoverview')
class DesignOverviewHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            RQ = obj.ResearchQuestion
            IV = obj.IndependentVariable
            DV = obj.DependentVariable
            var3 = obj.ThirdVariable
            var4 = obj.FourthVariable
            var5 = obj.FifthVariable
            IVType = obj.IndependentVariableType
            DVType = obj.DependentVariableType
            var3Type = obj.ThirdVariableType
            var4Type = obj.FourthVariableType
            var5Type = obj.FifthVariableType
            IVUnits = obj.IndependentVariableUnits
            DVUnits = obj.DependentVariableUnits
            var3Units = obj.ThirdVariableUnits
            var4Units = obj.FourthVariableUnits
            var5Units = obj.FifthVariableUnits
            IVScaleMin = obj.IndependentVariableScaleMinimum
            IVScaleMax = obj.IndependentVariableScaleMaximum
            DVScaleMin = obj.DependentVariableScaleMinimum
            DVScaleMax = obj.DependentVariableScaleMaximum
            var3ScaleMin = obj.ThirdVariableScaleMinimum
            var3ScaleMax = obj.ThirdVariableScaleMaximum
            var4ScaleMin = obj.FourthVariableScaleMinimum
            var4ScaleMax = obj.FourthVariableScaleMaximum
            var5ScaleMin = obj.FifthVariableScaleMinimum
            var5ScaleMax = obj.FifthVariableScaleMaximum
            IVBinary1 = obj.IndependentVariableBinary1
            IVBinary2 = obj.IndependentVariableBinary2
            DVBinary1 = obj.DependentVariableBinary1
            DVBinary2 = obj.DependentVariableBinary2
            var3Binary1 = obj.ThirdVariableBinary1
            var3Binary2 = obj.ThirdVariableBinary2
            var4Binary1 = obj.FourthVariableBinary1
            var4Binary2 = obj.FourthVariableBinary2
            var5Binary1 = obj.FifthVariableBinary1
            var5Binary2 = obj.FifthVariableBinary2
            doRender(self, 'designoverview.htm', {'RQ': RQ, 'IV': IV, 'DV': DV, 'var3': var3, 'var4': var4, 'var5': var5,
            'IVType': IVType, 'DVType': DVType, 'var3Type': var3Type, 'var4Type': var4Type, 'var5Type': var5Type, 'IVUnits': IVUnits,
            'DVUnits': DVUnits, 'var3Units': var3Units, 'var4Units': var4Units, 'var5Units': var5Units,
            'IVScaleMin': IVScaleMin, 'IVScaleMax': IVScaleMax, 'DVScaleMin': DVScaleMin, 'DVScaleMax': DVScaleMax, 'var3ScaleMin': var3ScaleMin,
            'var3ScaleMax': var3ScaleMax, 'var4ScaleMin': var4ScaleMin, 'var4ScaleMax': var4ScaleMax, 'var5ScaleMin': var5ScaleMin, 'var5ScaleMax': var5ScaleMax,
            'IVBinary1': IVBinary1, 'IVBinary2': IVBinary2, 'DVBinary1': DVBinary1, 'DVBinary2': DVBinary2, 'var3Binary1': var3Binary1,
            'var4Binary1': var4Binary1, 'var4Binary2': var4Binary2, 'var5Binary1': var5Binary1, 'var5Binary2': var5Binary2})
     # TODO Redirect to questionivdvpage if they click a certain button
    def post(self):
        self.session=get_current_session()
        if (self.request.get('EditDesign')):
            return webapp2.redirect('/home')
        elif (self.request.get('EditNotifications')):
            return webapp2.redirect('/notificationsettings')
        else:
            return webapp2.redirect('/dailyreport')
# Handler for page that explains the different types of variables
class VariableTypeExplanationsHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            doRender(self, 'variabletypeexplanations.htm')
class DesignSuccessfulHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            doRender(self, 'design_successful.htm')

class NotificiationSettingsHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            doRender(self, 'notificationsettings.htm')
    def post(self):
        self.session=get_current_session()
        return webapp2.redirect('/notificationsettings')
class DailyReportHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            dorender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            RQ = obj.ResearchQuestion
            IV = obj.IndependentVariable
            DV = obj.DependentVariable
            var3 = obj.ThirdVariable
            var4 = obj.FourthVariable
            var5 = obj.FifthVariable
            IVType = obj.IndependentVariableType
            DVType = obj.DependentVariableType
            var3Type = obj.ThirdVariableType
            var4Type = obj.FourthVariableType
            var5Type = obj.FifthVariableType
            IVUnits = obj.IndependentVariableUnits
            DVUnits = obj.DependentVariableUnits
            var3Units = obj.ThirdVariableUnits
            var4Units = obj.FourthVariableUnits
            var5Units = obj.FifthVariableUnits
            IVScaleMin = obj.IndependentVariableScaleMinimum
            IVScaleMax = obj.IndependentVariableScaleMaximum
            DVScaleMin = obj.DependentVariableScaleMinimum
            DVScaleMax = obj.DependentVariableScaleMaximum
            var3ScaleMin = obj.ThirdVariableScaleMinimum
            var3ScaleMax = obj.ThirdVariableScaleMaximum
            var4ScaleMin = obj.FourthVariableScaleMinimum
            var4ScaleMax = obj.FourthVariableScaleMaximum
            var5ScaleMin = obj.FifthVariableScaleMinimum
            var5ScaleMax = obj.FifthVariableScaleMaximum
            IVBinary1 = obj.IndependentVariableBinary1
            IVBinary2 = obj.IndependentVariableBinary2
            DVBinary1 = obj.DependentVariableBinary1
            DVBinary2 = obj.DependentVariableBinary2
            var3Binary1 = obj.ThirdVariableBinary1
            var3Binary2 = obj.ThirdVariableBinary2
            var4Binary1 = obj.FourthVariableBinary1
            var4Binary2 = obj.FourthVariableBinary2
            var5Binary1 = obj.FifthVariableBinary1
            var5Binary2 = obj.FifthVariableBinary2
            # these queries filter the data such that only the logged-in user gets included. To include all participants, remove the "DailyReportData.usernum == self.session['usernum']"
            DataReportQue=DataReport.query(DataReport.username == self.session['username'])
            # Order by date MinimumUTCTime, then day (number), then time of day (so if user reports data before the current time or even current day it's sorted)
            DataReportQue=DataReportQue.order(DataReport.usernum).order(-DataReport.MinimumUTCTime) # Added minues in front of DataReport.MinimumUTCTime (apparently needs a hyphen to specify descending order [ascending is default])
            DR=DataReportQue.fetch(7) # Get last 7 entries in the datastore (Need 7 at max when user logs in in the Evening)
            # DR = [3, 1, 3, 2, 2, 1, 1, 2, 1, 2, 1, 2]; # Placeholder for data

            # Credit to Attaque for finding time differences https://stackoverflow.com/a/47207182
            # Placeholder arrays for variable array values (daily report page doesn't use the optional variable array values if var4 and/or var5 )
            IVDRValues = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
            var3DRValues = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
            var4DRValues = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
            var5DRValues = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
            DVDRValues = [-1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0]
            if (DR): # Checks if the query returned any values
                DateTimeNow = datetime.datetime.now() # Time now (UTC) # Add " + datetime.timedelta(hours = 6)" to statement to test if data points are moved as time passes
                TimezoneOffset = DR[0].TimezoneOffset
                DateTimeNowLocal = DateTimeNow - datetime.timedelta(minutes = TimezoneOffset) # Time now (user's local timezone according to their last report)
                DateTimeNowLocalHour = int(DateTimeNowLocal.hour) # Hour
                # Set minimum hour needed to report for a certain time of day
                if (DateTimeNowLocalHour >= 0 and DateTimeNowLocalHour <= 5): # Night
                    DateTimeNowLocal = DateTimeNowLocal.replace(hour = 0, minute=0, second=0)
                elif (DateTimeNowLocalHour >= 6 and DateTimeNowLocalHour <= 11): # Morning
                    DateTimeNowLocal = DateTimeNowLocal.replace(hour = 6, minute=0, second=0)
                elif (DateTimeNowLocalHour >= 12 and DateTimeNowLocalHour <= 17): # Afternoon
                    DateTimeNowLocal = DateTimeNowLocal.replace(hour = 12, minute=0, second=0)
                elif (DateTimeNowLocalHour >= 18 and DateTimeNowLocalHour <= 23): # Evening
                    DateTimeNowLocal = DateTimeNowLocal.replace(hour = 18, minute=0, second=0)
                else:
                    pass
                DateTimeNowUTC = DateTimeNowLocal + datetime.timedelta(minutes = TimezoneOffset) # Apply offset to time that's been rounded down
                j = 0 # Keeps track of where in the placeholder array we are
                # Cycle through the last seven (possibly less) reports
                for i in range(0, len(DR)):
                    # Credit to Attaque for finding time difference in certain units https://stackoverflow.com/a/47207182
                    if (TimezoneOffset > 0):
                        timeDifference = DateTimeNowUTC - (DR[i].MinimumUTCTime)
                    elif (TimezoneOffset < 0):
                        timeDifference = DateTimeNowUTC - (DR[i].MinimumUTCTime)
                    else:
                        pass
                    timeDifferenceInSeconds = timeDifference.total_seconds()
                    timeDifferenceInHours = divmod(timeDifferenceInSeconds, 3600)[0] # Get time difference in hours
                    # Put value of report into the array with index based on the difference between the most recent report and the report before that
                    if (timeDifferenceInHours < 6):
                        if (j < 7): # Don't do anything
                            pass
                    elif (timeDifferenceInHours >= 6 and timeDifferenceInHours <= 11): # Push report 1 index to the right
                        j+=1
                        DateTimeNowUTC = DateTimeNowUTC - datetime.timedelta(hours = 6) # Go to next nearest time of day
                    elif (timeDifferenceInHours >= 12 and timeDifferenceInHours <= 17): # Gap of 1
                        j+=2
                        DateTimeNowUTC = DateTimeNowUTC - datetime.timedelta(hours = 12) # Go to next nearest time of day
                    elif (timeDifferenceInHours >= 18 and timeDifferenceInHours <= 23): # Gap of 2
                        j+=3
                        DateTimeNowUTC = DateTimeNowUTC - datetime.timedelta(hours = 18) # Go to next nearest time of day
                    elif (timeDifferenceInHours >= 24 and timeDifferenceInHours <= 29): # Gap of 3
                        j+=4
                        DateTimeNowUTC = DateTimeNowUTC - datetime.timedelta(hours = 24) # Go to next nearest time of day
                    elif (timeDifferenceInHours >= 30 and timeDifferenceInHours < 35): # Gap of 4
                        j+=5
                        DateTimeNowUTC = DateTimeNowUTC - datetime.timedelta(hours = 30) # Go to next nearest time of day
                    elif (timeDifferenceInHours >= 36 and timeDifferenceInHours <= 41): # Gap of 5
                        j+=6
                        DateTimeNowUTC = DateTimeNowUTC - datetime.timedelta(hours = 36) # Go to next nearest time of day
                    else:
                        print("Gap calculation too large")
                    if (DR[i].IndependentVariableReportData != None):
                        IVDRValues[j] = DR[i].IndependentVariableReportData
                    if (DR[i].ThirdVariableReportData != None):
                        var3DRValues[j] = DR[i].ThirdVariableReportData
                    if (DR[i].DependentVariableReportData != None):
                        DVDRValues[j] = DR[i].DependentVariableReportData
                    if (DR[i].FourthVariableReportData != None):
                        if (var4 != None): # Check if the user has a 2nd Third Variable (alt. cause 2)
                            var4DRValues[j] = DR[i].FourthVariableReportData
                    if (DR[i].FifthVariableReportData != None): # Check if the user has a 3rd Third Variable (alt. cause 3)
                        if (var5 != None):
                            var5DRValues[j] = DR[i].FifthVariableReportData
                    DateTimeNowUTC = DateTimeNowUTC - datetime.timedelta(hours = 6) # Go to next nearest time of day corresponding to a certain time frame in hours
                    j+=1 # Go to the next index (don't account for gaps)
            doRender(self, 'dailyreport.htm', {'RQ': RQ, 'IV': IV, 'DV': DV, 'var3': var3, 'var4': var4, 'var5': var5,
            'IVType': IVType, 'DVType': DVType, 'var3Type': var3Type, 'var4Type': var4Type, 'var5Type': var5Type,
            'IVUnits': IVUnits, 'DVUnits': DVUnits, 'var3Units': var3Units, 'var4Units': var4Units, 'var5Units': var5Units,
            'IVScaleMin': IVScaleMin, 'IVScaleMax': IVScaleMax, 'DVScaleMin': DVScaleMin, 'DVScaleMax': DVScaleMax, 'var3ScaleMin': var3ScaleMin,
            'var3ScaleMax': var3ScaleMax, 'var4ScaleMin': var4ScaleMin, 'var4ScaleMax': var4ScaleMax, 'var5ScaleMin': var5ScaleMin,
            'var5ScaleMax': var5ScaleMax, 'IVBinary1': IVBinary1, 'IVBinary2': IVBinary2,
            'DVBinary1': DVBinary1, 'DVBinary2': DVBinary2, 'var3Binary1': var3Binary1, 'var3Binary2': var3Binary2,
            'var4Binary1': var4Binary1, 'var4Binary2': var4Binary2, 'var5Binary1': var5Binary1, 'var5Binary2': var5Binary2,
            'IVDRValues': IVDRValues, 'var3DRValues': var3DRValues, 'var4DRValues': var4DRValues, 'var5DRValues': var5DRValues, 'DVDRValues': DVDRValues})
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        TimeOfDay = self.request.get('TimeOfDay') # Get time of day index
        # Credit to TheOne for parsing JS time for Python https://stackoverflow.com/q/8153631
        JSMinimumUTCTime = self.request.get('MinimumUTCTime') # Get minimum Date/Time for the time frame the user logged in (Night, Morning, etc.)
        TimezoneOffset = self.request.get('TimezoneOffset')
        if (JSMinimumUTCTime != ""):
            PythonMinimumUTCTime = datetime.datetime.strptime(JSMinimumUTCTime, "%a, %d %b %Y %H:%M:%S %Z") # Holds UTC time to decrement as we move from report to report (Night to Evening to Afternoon to Morning)
        if (TimeOfDay != ""):
            TimeOfDay = int(TimeOfDay)
        if (TimezoneOffset != ""):
            TimezoneOffset = int(TimezoneOffset)
        ExactUTCTime = datetime.datetime.now() # The EXACT time a data point was reported
        # TODO Put the report into the datastore only if an entry hasn't been put in for the time specified
        # these queries filter the data such that only the logged-in user gets included. To include all participants, remove the "DataReportData.usernum == self.session['usernum']"
        DataReportQue=DataReport.query(DataReport.username == self.session['username'])
        # Order by date and minimum time needed to report for a certain time of day, then day (number), then time of day (so if user reports data before the current time or even current day it's sorted)
        DataReportQue=DataReportQue.order(DataReport.usernum).order(-DataReport.MinimumUTCTime) # Added minues in front of DataReport.MinimumUTCTime (apparently needs a hyphen to specify descending order [ascending is default])
        DR=DataReportQue.fetch(7) # Get last 7 entries in the datastore (Need 7 at max when user logs in in the Evening)
        variablesArray = ["IV", "var3", "var4", "var5", "DV"]
        timeOfDayStringArray = ["Night", "Morning", "Afternoon", "Evening"]

        for i in range(0, 7): # Loop over every time of day for each variable (append number to initial string to get the right name)
            UserDataReport = DataReport() # New DataReport which will be stored in the Google Datastore (has columns for every variable)
            for j in range(0, 5): # Outer loop that cycles through variables
                DailyReportString = variablesArray[j] + "DailyReport" # Create string to use to get reports for each variable
                VariableDailyReportString = DailyReportString + str(i) # Append integer to variable report string (used to get report of a variable for a specific time of day)
                DailyReport = self.request.get(VariableDailyReportString) # Get a data point for a variable (ex. IVDailyReport3, var3DailyReport0)
                if (DailyReport != None and DailyReport != ""): # Check if anything is returned
                    UserDataReport.usernum = self.session['usernum'] # Set usernum
                    UserDataReport.username = self.session['username'] # Set username
                    modularTime = TimeOfDay % 4 # Determines what time of day the report is for with modular division
                    UserDataReport.timeOfDayInt = modularTime # Set "time of day" as an integer (0=Night, 1=Morning, 2=Afternoon, 3=Evening)
                    UserDataReport.timeOfDayString = timeOfDayStringArray[modularTime] # Assign "time of day" (Night, Morning, etc. using values in array)
                    if (DailyReportString == "IVDailyReport"):
                        UserDataReport.IndependentVariableReportData = float(DailyReport) # Put report value into column
                    elif (DailyReportString == "var3DailyReport"):
                        UserDataReport.ThirdVariableReportData = float(DailyReport)
                    elif (DailyReportString == "var4DailyReport"):
                        UserDataReport.FourthVariableReportData = float(DailyReport)
                    elif (DailyReportString == "var5DailyReport"):
                        UserDataReport.FifthVariableReportData = float(DailyReport)
                    elif (DailyReportString == "DVDailyReport"):
                        UserDataReport.DependentVariableReportData = float(DailyReport)
                    else:
                        logging.info("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX DailyReport Name not found on the page")
                    UserDataReport.TimezoneOffset = TimezoneOffset # Set offset between local timezone and UTC in minutes
                    UserDataReport.MinimumUTCTime = PythonMinimumUTCTime # If it's the first (0) report, use the minimum time the user could've logged in to get the time (Night, Morning, etc.)
                    entityExists = False; # Boolean value that changes based on if a report already exists in the datastore by checking "MinimumUTCTime" value
                    # Loop through the list of fetched DataReports (doesn't loop if the IVDR list is empty [length of 0?])
                    for k in range (0, len(DR)):
                        if (UserDataReport.MinimumUTCTime == DR[k].MinimumUTCTime): # User already made a report for that time of day
                            if (DailyReportString == "IVDailyReport"):
                                DR[k].IndependentVariableReportData = UserDataReport.IndependentVariableReportData # Overwrite report value
                            elif (DailyReportString == "var3DailyReport"):
                                DR[k].ThirdVariableReportData = UserDataReport.ThirdVariableReportData # Overwrite report value
                            elif (DailyReportString == "var4DailyReport"):
                                DR[k].FourthVariableReportData = UserDataReport.FourthVariableReportData # Overwrite report value
                            elif (DailyReportString == "var5DailyReport"):
                                DR[k].FifthVariableReportData = UserDataReport.FifthVariableReportData # Overwrite report value
                            elif (DailyReportString == "DVDailyReport"):
                                DR[k].DependentVariableReportData = UserDataReport.DependentVariableReportData # Overwrite report value
                            else:
                                logging.info("XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")
                                logging.info("DailyReport Name not found on the page")
                            DR[k].put() # Put the UPDATED entity into the datastore with overwritten report value (id and everything else remains the same)
                            entityExists = True; # User has already reported for this time of day
                            break # Exit for loop once we've found an entity with a report for a specific time of day
                    if (not entityExists): # Put NEW entity into the datastore if there's no report for that time of day
                        UserDataReport.put()
                        logging.info("XXXXXXXXXXXXXXXXXXXXXX")
                        logging.info("New DataReport put into the DataStore")
                else: # Print to log that nothing was returned from the webpage
                    logging.info("XXXXXXXXXXXXXXXXX")
                    logging.info("Nothing returned from webpage")
            # Subtract six hours since we're going from one time frame in the past (This Aftternoon to This Mornign and so on) (gives error message according to AJAX but data is stored properly)
            # PythonYear = PythonMinimumUTCTime.year
            # PythonMonth = PythonMinimumUTCTime.month
            # PythonDay = PythonMinimumUTCTime.day
            # PythonHour = PythonMinimumUTCTime.hour
            # PythonMinute = PythonMinimumUTCTime.minute
            # PythonMinimumUTCTime.second
            # TempPythonMinimumUTCTime = datetime.datetime(PythonYear, PythonMonth, PythonDay, PythonHour) # Create new datetime object that has 6 hours subtracted from it
            PythonMinimumUTCTime = PythonMinimumUTCTime - datetime.timedelta(hours=6)# Reassigning datetime value
            TimeOfDay = TimeOfDay-1 # Decrement time of day
        obj.put()
        return webapp2.redirect('/home')
class Day7QuestionsHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            dorender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            return doRender(self, 'day7questions.htm')
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        return webapp2.redirect('saving_data_post_success')
class Day14QuestionsHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            dorender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            return doRender(self, 'day14questions.htm')
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        return webapp2.redirect('saving_data_post_success')
class Day21QuestionsHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            dorender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            return doRender(self, 'day14questions.htm')
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        return webapp2.redirect('saving_data_post_success')
class RmQuestions1Handler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            doRender(self, 'rmquestions1.htm')
    def post(self):
        self.session=get_current_session()
        Question1 = self.request.get('Question1')
        Question2 = self.request.get('Question2')
        Question3 = self.request.get('Question3')
        Question4 = self.request.get('Question4')
        Question5 = int(self.request.get('Question5'))
        Question6 = 0;
        if (self.request('Question6').equals('yes')):
            Question6 = 1;
        else:
            Question6 = 0;
        Question7=String(self.request('Question7'))

        obj = self.session['userkey'].get()
        # Assign values to matrix
        Day = obj.Day

        obj.put()
        return webapp2.redirect('/rmquestions2.htm')
# Handler for the second set of Research Method Questions
class RmQuestions2Handler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            doRender(self, 'rmquestions2.htm')
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        Day = obj.UserDay
        Question8=self.request.get('Question8')
        Question9=self.request.get('Question9')
        Day = obj.Day

        obj.put()
        return webapp2.redirect('/')
class MultiYAxesGraphHandler(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            obj = self.session['userkey'].get()
            IV = obj.IndependentVariable
            DV = obj.DependentVariable
            var3 = obj.ThirdVariable
            var4 = obj.FourthVariable
            var5 = obj.FifthVariable
            DataReportQue=DataReport.query(DataReport.username == self.session['username'])
            # Order by date MinimumUTCTime, then day (number), then time of day (so if user reports data before the current time or even current day it's sorted)
            DataReportQue=DataReportQue.order(DataReport.usernum).order(DataReport.MinimumUTCTime)
            DataReportAllValues = DR=DataReportQue.fetch()
            IVAllValues = []
            var3AllValues = []
            var4AllValues = []
            var5AllValues = []
            DVAllValues = []

            # Loop through the rows of DataReports and get values for each variable for each time of day for every day data has been reported
            for i in range (0, len(DataReportAllValues)):
                # If there is no data for a particular time of a day for a specific variable, put a sentinel value of 1 in the array(s)
                if (DataReportAllValues[i].IndependentVariableReportData != None):
                    IVAllValues.append(-1)
                else:
                    IVAllValues.append(DataReportAllValues[i].IndependentVariableReportData)

                if (DataReportAllValues[i].ThirdVariableReportData != None):
                    var3AllValues.append(-1)
                else:
                    var3AllValues.append(DataReportAllValues[i].ThirdVariableReportData)

                if (DataReportAllValues[i].FourthVariableReportData != None):
                    var4AllValues.append(-1)
                else:
                    var4AllValues[i].append(DataReportAllValues[i].FourthVariableReportData)

                if (DataReportAllValues[i].FifthVariableReportData != None):
                    var5AllValues.append(-1)
                else:
                    var5AllValues.append(DataReportAllValues[i].FifthVariableReportData)

                if (DataReportAllValues[i].DependentVariableReportData != None):
                    DVAllValues.append(-1)
                else:
                    DVAllValues[i].append(DataReportAllValues[i].DependentVariableReportData)

            doRender(self, 'multiyaxesgraph.htm', {'IV': IV, 'DV': DV, 'var3': var3,
            'var4': var4, 'var5': var5, 'IVAllValues': IVAllValues, 'var3AllValues': var3AllValues,
            'var4AllValues': var4AllValues, 'var5AllValues': var5AllValues, 'DVAllValues': DVAllValues})
    def post(self):
        self.session=get_current_session()
        obj = self.session['userkey'].get()
        return webapp2.redirect('/')
# TODO Fix Twilio syntax errors (maybe different version needed?)
class SendSMSHandler(webapp.RequestHandler):
    def post(self):
        message = twiml.Response()
        message.say("Bottom Text")
        self.response.headers['Content-Type'] = 'text/xml'
        self.response.write(str(message))
class SendSMSHandler2(webapp.RequestHandler):
    def get(self):
        self.session=get_current_session()
        if not self.session.is_active():
            doRender(self, 'login.htm')
        else:
            # Your Account SID from twilio.com/console
            account_sid = "ACd09296a63dcc1fedb108846285750472"
            # Your Auth Token from twilio.com/console
            auth_token  = "1f810944f25f96c1367ad26268e91a18"
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                to="+18149321630",
                from_="+18142124052",
                body="This is a twilio test")
            print(message.sid)
            doRender(self, 'dailyreport.htm')


application = webapp2.WSGIApplication([
    # Debugging
    ('/logging', LoggingHandler),

    # Users
    ('/user_create', UserCreateHandler),
    ('/user_verify_logged_in', UserVerifyLoggedInHandler),
    ('/login', LoginHandler),
    ('/logout', LogoutHandler),

    # Condition Randomization and Stimuli Presentation
    ('/stimuli_presentation', StimuliPresentationHandler),

    # Saving Data to the Datastore
    ('/saving_data_post', SavingDataPostHandler),
    ('/saving_data_post_success', SavingDataPostSuccessHandler),
    ('/saving_data_ajax', SavingDataAjaxHandler),

    # Pages (and handlers) added by Matthew Dodson https://github.com/mjd119
    ('/overview', OverviewHandler),
    ('/home', HomeHandler),
    ('/variabletypeexplanations', VariableTypeExplanationsHandler),
    ('/questionivdv', QuestionIVDVHandler),
    ('/chooseextravariables', ChooseExtraVariablesHandler),
    ('/selectvariabletype', SelectVariableTypeHandler),

    ('/choosedailyquestions', ChoooseDailyQuestionsHandler),
    ('/designoverview', DesignOverviewHandler),
    ('/notificationsettings', NotificiationSettingsHandler),
    ('/design_successful', DesignSuccessfulHandler),
    ('/dailyreport', DailyReportHandler),
    # ('/choosescale', ChooseScaleHandler),
    # ('/choosevariableunits', ChooseVariableUnitsHandler),
    # ('/choosebinaries', ChooseBinariesHandler),
    # ('/dvdailyreport', DVDailyReportHandler),
    # ('/var3dailyreport', Var3DailyReportHandler),
    # ('/var4dailyreport', Var4DailyReportHandler),
    # ('/var5dailyreport', Var5DailyReportHandler),
    ('/rmquestions1', RmQuestions1Handler),
    ('/rmquestions2', RmQuestions2Handler),
    ('/multiyaxesgraph', MultiYAxesGraphHandler),
    ('/twiml', SendSMSHandler),
    ('/send_sms', SendSMSHandler2),
    # End credit

    # Seeing and Downloading Data
    ('/downloading_data', DownloadingDataHandler),

    # Linking with Mturk
    ('/mturkid', MturkIDHandler),
    ('/do_not_qualify', DNQHandler),

    # Ensuring that the order of the study is followed - tracking progress within a page
    ('/tracking_progress_within_a_page_with_HTML5_Web_Storage', TrackingProgressWithinAPageWithHTML5WebStorage),
    ('/tracking_progress_within_a_page_with_AJAX_and_sessions', TrackingProgressWithinAPageWithAJAXAndSessions),
    ('/tracking_progress_within_a_page_with_AJAX_and_the_datastore', TrackingProgressWithinAPageWithAJAXAndTheDatastore),

    # Ensuring that the order of the study is followed - tracking progress across page
    ('/recording_each_page_load_page_1', RecordingEachPageLoadPage1Handler),
    ('/recording_each_page_load_page_2', RecordingEachPageLoadPage2Handler),
    ('/recording_each_page_load_page_3', RecordingEachPageLoadPage3Handler),
    ('/using_cookies_to_keep_the_user_from_going_back', UsingCookiesToKeepTheUserFromGoingBackHandler),

    # Piping Text

    # Communicating with Mturk Servers
    ('/boto_get_account_balance', BotoGetAccountBalanceHandler),
    ('/boto_querying_a_hit', BotoQueryingAHitHandler),

    # Fixed Width
    ('/nonresponsive', NonResponsiveHandler),

    # Useful Resources
    ('/demographics', DemographicsHandler),

    # All other urls get redirected to the overview
    ('/.*', HomeHandler)],
	debug=True)

def main():
	run_wsgi_app(application)


if __name__ == '__main__':
  main()
