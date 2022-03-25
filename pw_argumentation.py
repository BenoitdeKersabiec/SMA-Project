import sys
sys.path.append('communication')

from mesa import Model
from mesa.time import RandomActivation


from communication.agent.CommunicatingAgent import CommunicatingAgent
from communication.message.Message import Message
from communication.message.MessageService import MessageService
from communication.message.MessagePerformative import MessagePerformative
from communication.preferences.Preferences import Item, Preferences, CriterionName, CriterionValue
from communication.preferences.Value import Value
from random import shuffle


class ArgumentAgent(CommunicatingAgent):
    """ TestAgent which inherit from CommunicatingAgent.
    """
    def __init__(self, unique_id, model, name, preference):
        super().__init__(unique_id, model, name)
        self.preference = preference
        self.state = 'None'

    def step(self):
        super().step()
        inbox = self.receive_message()
        for in_message in inbox:
            if in_message.get_performative().name == "PROPOSE":
                if self.preference.is_item_among_top_10_percent(received[-1].get_content(), self.model.item_list):
                    out_respond = Message(self.get_name(), in_message.get_exp(), MessagePerformative(102), in_message.get_content())
                    print(self.get_name(), "sending message:")
                    print(out_respond)
                    self.send_message(out_respond)
                    self.state="Accepted"
                else:
                    out_respond = Message(self.get_name(), in_message.get_exp(), MessagePerformative(104), in_message.get_content())
                    print(out_respond)
                    self.send_message(out_respond)
            if in_message.get_performative().name == "COMMIT" and self.state == "Accepted":
                out_respond = Message(self.get_name(), in_message.get_exp(), MessagePerformative(103), in_message.get_content())
                print(out_respond)
                self.send_message(out_respond)




    def get_preference(self):
        return self.preference

    #TODO faire une fonction qui génère les préférences du sujet (pas random)

    def generate_preferences(self, list_items):
        self.preference.set_criterion_name_list(self.generate_random_criterions_list())
        for item in list_items:
            self.generate_preferences_item(item)
        
    def generate_random_criterions_list(self):
        crit_names = list(CriterionName)
        shuffle(crit_names)
        return crit_names

    def generate_preferences_item(self, item):
        for critname in CriterionName:
            self.preference.add_criterion_value(CriterionValue(item, critname, self.generate_random_value()))

    def generate_random_value(self):
        values_list = list(Value)
        shuffle(values_list)
        return values_list[0]




class ArgumentModel(Model):
    """ ArgumentModel which inherit from Model.
    """
    def __init__(self):
        self.schedule = RandomActivation(self)
        self.__messages_service = MessageService(self.schedule)

        # To be completed
        diesel_engine = Item("Diesel Engine", "A super cool diesel engine")
        electric_engine = Item("Electric Engine", "A very quiet engine")
        self.item_list = [diesel_engine, electric_engine]
        
        self.A1 = ArgumentAgent(1, self, 'Alice', Preferences())
        self.A2 = ArgumentAgent(2, self, 'Bob', Preferences())

        self.A1.generate_preferences(self.item_list)
        self.A2.generate_preferences(self.item_list)

        self.schedule.add(self.A1)
        self.schedule.add(self.A2)
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages(self.A1, self.A2, )
        self.schedule.step()


if __name__ == "__main__":
    argument_model = ArgumentModel()

    message = Message("Alice", "Bob", MessagePerformative(101), argument_model.item_list[1])
    print(message)
    argument_model.A1.send_message(message)
    received = argument_model.A2.get_new_messages()
    if argument_model.A2.preference.is_item_among_top_10_percent(received[-1].get_content(), argument_model.item_list):
        respond = Message("Bob", "Alice", MessagePerformative(102), received[-1].get_content())
        print(respond)
        argument_model.A2.send_message(respond)
    else:
        respond = Message("Bob", "Alice", MessagePerformative(104), received[-1].get_content())
        print(respond)
        argument_model.A2.send_message(respond)
    # To be completed
