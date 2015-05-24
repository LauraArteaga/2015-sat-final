from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Template, Context
from django.template.loader import get_template
from django.contrib.auth import authenticate, logout, login

from bs4 import BeautifulSoup

from models import Event
from models import Intermediary
from models import User
from models import Update

import urllib
import datetime
import time


def getXML():
	url = "http://datos.madrid.es/portal/site/egob/menuitem.ac61933d6ee3c31cae77ae7784f1a5a0/?vgnextoid=00149033f2201410VgnVCM100000171f5a0aRCRD&format=xml&file=0&filename=206974-0-agenda-eventos-culturales-100&mgmtid=6c0b6d01df986410VgnVCM2000000c205a0aRCRD"
	xml = urllib.urlopen(url).read()
	soup = BeautifulSoup(xml, "xml")
	
	return soup

def getEvent(line):
	title = line.find(nombre="TITULO").string
	
	try:
		price = line.find(nombre="PRECIO").string
	except:
		price = "Gratuito"

	try:
		eventType = line.find(nombre="TIPO").string
		eventType = eventType.split("actividades/")[1]
	except:
		eventType = "No especificado"
			
	hour = line.find(nombre="HORA-EVENTO").string

	hourEnd = line.find(nombre="FECHA-FIN-EVENTO").string
	hourEnd = hourEnd.split(" ")[0]
	hourEnd = hourEnd + " 23:59:00+00:00"

	try:
		description = line.find(nombre="DESCRIPCION").string
	except:
		description = "No hay informacion adicional para este evento"
		
	date = line.find(nombre="FECHA-EVENTO").string
	date = date.split(" ")[0]

	dateTime = date + " " + hour + ":00+00:00"
			
	try:
		duration = line.find(nombre="EVENTO-LARGA-DURACION").string
		if (duration == "0"):
			duration = "Evento de corta duracion"
		else:
			duration = "Evento de larga duracion"
	except:
		duration = "No especificada"
	
	try:		
		url = line.find(nombre="CONTENT-URL").string
	except:
		url = "http://localhost:1234/informacionNoDisponible"
	
	
	return (title, dateTime, hourEnd, price, eventType, duration, description, url)
	
def addEvents():
	xml = getXML()
	
	updateHour =  datetime.datetime.now()
	entry = Update(hour=updateHour)
	entry.save()
	
	content = xml.findAll("contenido")
	numEvents = len(content)

	for line in content:
		(title, dateTime, hourEnd, price, eventType, duration, description, url) = getEvent(line)
		entry = Event(title=title, date=dateTime, dateEnd=hourEnd, price=price, eventType=eventType, duration=duration, description=description, url=url, likes=0)
		entry.save()

def update(request):
	xml = getXML()
	
	updateHour =  datetime.datetime.now()
	entry = Update.objects.get(id=1)
	entry.hour = updateHour
	entry.save()
	
	content = xml.findAll("contenido")
	
	events = Event.objects.all()
	
	for line in content:
		(title, dateTime, hourEnd, price, eventType, duration, description, url) = getEvent(line)
		
		found = False
		for event in events:
			if (event.title == title):
				if (str(event.date) == str(dateTime)):
					found = True

		if (found == False):
			entry = Event(title=title, date=dateTime, dateEnd=hourEnd, price=price, eventType=eventType, duration=duration, url=url, description=description, likes=0)
			entry.save()

	return HttpResponseRedirect("/todas")

def emptyInfo(request):
	
	return HttpResponseRedirect("/todas")		
	
def add(request, eventID):
	username = request.user.username
	events = Intermediary.objects.filter(username=username)
	found = False

	for user in events:
		if str(user.eventID) == str(eventID):
			found = True
			
	if found == False:
		entry = Intermediary(username=username, eventID=eventID, date=datetime.datetime.now())
		entry.save()
	
	return HttpResponseRedirect("/todas")

def eventPage(request, eventID):
	entry = Event.objects.get(id=eventID)
	
	if request.user.is_authenticated():
		isAuthenticated = True
		username = request.user.username
	else:
		isAuthenticated = False
		username = None
		
	template = get_template('plantillaEvento.html')
	response = template.render(Context({'entry':entry,
										'isAuthenticated':isAuthenticated, 
										'username': username}))
	
	return HttpResponse(response)

def like(request, eventID):
	entry = Event.objects.get(id=eventID)
	likesOld = entry.likes
	entry.likes = likesOld + 1
	entry.save()
	
	return HttpResponseRedirect("/")
	
def help(request):
	if request.user.is_authenticated():
		isAuthenticated = True
		username = request.user.username
	else:
		isAuthenticated = False
		username = None
	
	template = get_template('plantillaAyuda.html')
	response = template.render(Context({'isAuthenticated':isAuthenticated, 
										'username': username}))
	return HttpResponse(response)
	
def allEvents(request):
		
	hourDB = Update.objects.get(id=1)
	hourUpdate = hourDB.hour

	if request.user.is_authenticated():
		isAuthenticated = True
		username = request.user.username
	else:
		isAuthenticated = False
		username = None

	if request.method == "GET":
		events = Event.objects.all()
		
	elif request.method == "POST":

		body = request.body.split("type=")
		filterType = body[1].split("&")[0]

		if filterType == "fecha":
			events = Event.objects.order_by("date")
		elif filterType == "peliculas":
			events = Event.objects.filter(eventType__exact="Peliculas")
		elif filterType == "actInf":
			events = Event.objects.filter(eventType__exact="ActividadesInfantiles")
		elif filterType == "gratis":
			events = Event.objects.filter(price__exact="Gratuito")
		elif filterType == "likes":
			events = Event.objects.order_by("-likes")
		else:
			events = Event.objects.filter(title__icontains=filterType)
		
	numEvents = len(events)
	template = get_template('plantillaTodosEventos.html')
	response = template.render(Context({'events':events,
										'hour':hourUpdate,
										'numEvents': numEvents,
										'isAuthenticated':isAuthenticated, 
										'username': username}))
	
	return HttpResponse(response)

def changeInfo(request):
	username = request.user.username
	
	if request.method == "POST":
		change = request.body.split("=")[0]
		changeType = request.body.split("=")[1]
		if change == "title":
			title = changeType.split("+")
			titleNew = ""
			for word in range(len(title)):
				titleNew += title[word] + " "
				
			user = User.objects.get(name=username)
			user.title = titleNew

		elif change == "description":
			description = changeType.split("+")
			descriptionNew = ""
			for word in range(len(description)):
				descriptionNew += description[word] + " "
				
			user = User.objects.get(name=username)
			user.description = descriptionNew
	user.save()	
			
	return HttpResponseRedirect(username)
	
def userPage(request, user):
	
	if request.user.is_authenticated():
		isAuthenticated = True
		username = request.user.username
	else:
		isAuthenticated = False
		username = None
		
	userInfo = User.objects.get(name=user)

	events = Intermediary.objects.filter(username=user)

	if len(events) == 0:
		events = None
		allEvents = None
		foundEvents = False
	else:
		foundEvents = True
		allEvents = []
		for line in events:
			allEvents.append(Event.objects.get(id=line.eventID))
		
	isUser = False
	if username == user:
		isUser = True

	
	if request.method == "POST":
		change = request.body.split("=")[0]
		changeType = request.body.split("=")[1]

		if change == "colour":
			colour = changeType
			userInfo.colour = colour
			userInfo.save()
		elif change == "size":
			if changeType == "grande":
				size = "130%"
				userInfo.fontSize = size
			elif changeType == "pequeno":
				size = "70%"
				userInfo.fontSize = size
			userInfo.save()
		elif change == "lettercolour":
			lettercolour = changeType
			userInfo.letterColour = lettercolour
			userInfo.save()
		elif change == "reset":
			colour = "#FF0080"
			userInfo.colour = colour
			lettercolour = "black"
			userInfo.letterColour = lettercolour
			size = "100%"
			userInfo.fontSize = size
			userInfo.save()
	if isUser:
		colour = userInfo.colour
		lettercolour = userInfo.letterColour
		size = userInfo.fontSize
	else:
		lettercolour = "black"
		colour = "#FF0080"
		size = "100%"
		
	template = get_template('plantillaPaginaUsuario.html')
	response = template.render(Context({'user':userInfo,
										'hours': events,
										'foundEvents': foundEvents,
										'events': allEvents,
										'isAuthenticated':isAuthenticated, 
										'username': username,
										'isUser': isUser,
										'colour': colour,
										'size': size,
										'letterColour': lettercolour}))
										
	return HttpResponse(response)
	
def logIn(request):
	if request.method == "GET":
		events = Event.objects.order_by("date")[:10]
		template = get_template('plantillaLogin.html')
		response = template.render(Context({'events':events}))

		return HttpResponse(response)
	
	if request.method == "POST":
		body = request.body.split("url=")
		username = body[1].split("&")[0]
		password = body[2]

		user = authenticate(username=username, password=password)

		if user is None:
			return HttpResponseRedirect("/login")
		else:
			login(request, user)
			allUsers = User.objects.all()
			found = False
			for user in allUsers:
				if (user.name == username):
					found = True
					
			if not found:
				title = "Pagina de " + username
				description = "Pagina sin descripcion"
				colour = "#FF0080"
				letterColour = "black"
				fontSize = "100%"
				entry = User(name=username, title=title, description=description, colour=colour, letterColour=letterColour, fontSize=fontSize)
				entry.save()
				
			return HttpResponseRedirect("/")

def logOut(request):
	
	logout(request)

	return HttpResponseRedirect("/")
	
def principalPage(request):
	events = Event.objects.all()
	if (len(events) == 0):
		addEvents()
	
	if request.user.is_authenticated():
		isAuthenticated = True
		username = request.user.username
	else:
		isAuthenticated = False
		username = None
	
	users = User.objects.all()
	if (len(users) != 0):
		foundUsers = True
		print "foundUsers = TRUE"
	else:
		foundUsers = False	
		print "foundUsers = FALSE"
	
	events = Event.objects.order_by("dateEnd")[:10]
	template = get_template('plantillaPrincipal.html')
	response = template.render(Context({'events':events,
										'isAuthenticated':isAuthenticated,
										'username': username,
										'foundUsers': foundUsers,
										'users': users}))
	
	return HttpResponse(response)

