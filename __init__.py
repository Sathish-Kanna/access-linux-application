import os
import glob
import subprocess
import configparser as ConfigParser

from adapt.intent import IntentBuilder
from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.log import LOG

#####################################################################
#
# TESTS
#  1: launch availabel application
#  2: terminate runing application
#
# Sample:
#  launch firefox
#  terminate firefox
#
# TODO:
#  update close app command
#
#####################################################################

class SearchApp:
	def __init__(self):
		self.paths = ['/usr/share/applications/', '/usr/local/share/applications/', os.path.expanduser('~/.local/share/applications/')]
		self.dictList=[]
		for path in self.paths:
			for filename in glob.glob(path+'*.desktop'):
				self.dictList.append(self.readDesktopFile(filename))
		
	def readDesktopFile(self, path):
		entryList = ['Name', 'Keywords','GenericName', 'Comment', 'Exec', 'Icon']
		dictEntry={'Name':None,'Keywords':None, 'GenericName':None, 'Comment':None, 'Exec':None, 'Icon':None, 'Path':path}
		Config = ConfigParser.ConfigParser(strict=False)
		Config.read(path)
		for obj in entryList:
			try:
				dictEntry[obj] = Config.get('Desktop Entry', obj, raw=True)
			except:
				dictEntry[obj] = None
		return dictEntry
	
	def searchApp(self, appKey):
		searchIndex={}
		for dictEntry in self.dictList:
			point=0
			if appKey in dictEntry['Name'].lower():
				point=point+10
			if dictEntry['Keywords'] is not None and appKey in dictEntry['Keywords'].lower():
				point=point+5
			if dictEntry['GenericName'] is not None and appKey in dictEntry['GenericName'].lower():
				point=point+3
			if dictEntry['Comment'] is not None and appKey in dictEntry['Comment'].lower():
				point=point+3
			if point > 0:
				searchIndex[self.dictList.index(dictEntry)]=point
		return self.dictList[max(searchIndex, key=searchIndex.get)]['Exec']
		
class AccessingApp(MycroftSkill):
	def __init__(self):
		super(AccessingApp, self).__init__("AccessingApp")

	@intent_file_handler('launch.app.intent')
	def handle_launch_app(self, message):
		appName = message.data['app'].lower()
		obj = SearchApp()
		try:
			appOpen = obj.searchApp(appName)
		except:
			self.speak_dialog("Try in a different way")
			return
		cmd = appOpen+' & disown'
		try:
			subprocess.call(cmd, shell=True) # app launch command
			self.speak_dialog("app.launch", data={"app": appName})
		except Exception as e:
			self.speak_dialog("app.notexist", data={"app": appName})

	@intent_file_handler('terminate.app.intent')
	def handle_close_app(self, message):
		appName = message.data['app']
		cmd='pkill -f '+appName
		try:
			subprocess.call(cmd, shell=True) # app terminate command
			self.speak_dialog("app.terminate", data={"app": appName})

		except Exception as e:
			self.speak_dialog("app.notopen", data={"app": appName})

def create_skill():
    return AccessingApp()
