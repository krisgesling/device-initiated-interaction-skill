from datetime import datetime
from time import sleep
import requests 

from mycroft import MycroftSkill, intent_handler
from mycroft.audio import wait_while_speaking
from mycroft.util.format import nice_duration, TimeResolution

API_ENDPOINT = "https://example.com/api"
API_KEY = "XXXXXXXXXXXXXXXXX"
MINUTES = 60 # seconds
HOURS = 60 * MINUTES


class DeviceInitiatedInteraction(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        self.proning_event = "Proning protocol"
    

    def initialize(self):
        self.settings_change_callback = self.on_settings_changed


    def on_settings_changed(self):
        self.log.info("Trigger actions when settings are updated")


    @intent_handler('interaction.initiated.device.intent')
    def handle_interaction_initiated_device(self, message):
        self.cancel_scheduled_event(self.proning_event)
        # Schedule the proning protocol every two hours, starting immediately
        # https://mycroft-core.readthedocs.io/en/latest/source/mycroft.html?highlight=schedule#mycroft.MycroftSkill.schedule_repeating_event
        self.schedule_repeating_event(self.proning_protocol, datetime.now(), 2 * HOURS, name=self.proning_event)
        self.speak_dialog('interaction.initiated.device')

    
    def proning_protocol(self):
        self.speak_dialog('step.one')
        # Pause for duration of Text to Speech
        wait_while_speaking()
        # Pause an additional period for patient to complete step
        sleep(10)

        response = self.ask_yesno('confirm')
        if response == 'yes':
            self.speak_dialog('step.two')
        
        # Schedule non-recurring patient check in 15 minutes
        # Note: event time can be in seconds or a datetime
        # https://mycroft-core.readthedocs.io/en/latest/source/mycroft.html?highlight=schedule#mycroft.MycroftSkill.schedule_event
        self.schedule_event(self.check_on_patient, 30)


    def check_on_patient(self):
        response = self.get_response('get.feedback')
        self.send_patient_response(response)


    def send_patient_response(self, response):
        data = { 'api_key': API_KEY, 'patient_response':response } 
        r = requests.post( url=API_ENDPOINT, data=data ) 
        self.log.info("Sent feedback: {}".format(response))

    
    @intent_handler('when.is.next.protocol.intent')
    def handle_when_next(self, message):
        # Get the time remaining before our scheduled event
        # https://mycroft-core.readthedocs.io/en/latest/source/mycroft.html?highlight=get%20event#mycroft.MycroftSkill.get_scheduled_event_status
        secs_remaining = self.get_scheduled_event_status(self.proning_event) 
        if secs_remaining:
            self.speak_dialog('time.remaining', 
                              { 'duration': nice_duration(secs_remaining, 
                                resolution=TimeResolution.MINUTES) })


def create_skill():
    return DeviceInitiatedInteraction()