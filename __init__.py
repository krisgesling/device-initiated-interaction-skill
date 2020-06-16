from mycroft import MycroftSkill, intent_file_handler


class DeviceInitiatedInteraction(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('interaction.initiated.device.intent')
    def handle_interaction_initiated_device(self, message):
        self.speak_dialog('interaction.initiated.device')


def create_skill():
    return DeviceInitiatedInteraction()

