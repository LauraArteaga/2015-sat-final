from django.contrib.syndication.views import Feed
from DeLorean.models import  Event, Intermediary

class feedRSS(Feed):
	title="MIS EVENTOS"
	link="http://localhost:1234/"
	description="Eventos seleccionados pagina personal"
	
	def get_object(sel, request, username):
		return Intermediary.objects.filter(username=username)
	
	def items(self,obj):
		allEvents = []
		for line in obj:
			allEvents.append(Event.objects.get(id=line.eventID))
		return allEvents
		
	def item_title(self, item):
		return item.title
	
	def item_link(self, item):
		link = "http://localhost:1234/actividades/" + str(item.id)
		return link
