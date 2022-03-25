import sys
sys.path.append('.')

from mesa import Model
from mesa.time import RandomActivation


from agent.CommunicatingAgent import CommunicatingAgent
from message.Message import Message
from message.MessageService import MessageService
from message.MessagePerformative import MessagePerformative
from preferences.Preferences import Item, Preferences, CriterionName, CriterionValue
from preferences.Value import Value
from random import shuffle


class ArgumentAgent(CommunicatingAgent):
    """ TestAgent which inherit from CommunicatingAgent.
    """
    def __init__(self, unique_id, model, name, preference):
        super().__init__(unique_id, model, name)
        self.preference = preference

    def step(self):
        super().step()

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
        self.__message_performative = MessagePerformative()

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

        self.A1.send_message(Message(self.A1, self.A2, self.__message_performative.PROPOSE, self.item_list[0]))
        test = self.A2.get_new_messages()
        print("TEST", test)
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages(self.A1, self.A2, )
        self.schedule.step()


if __name__ == "__main__":
    argument_model = ArgumentModel()

    print(argument_model.item_list[0].get_value(argument_model.A1.preference, CriterionName.PRODUCTION_COST))
    print(argument_model.A1.preference.is_preferred_criterion(CriterionName.CONSUMPTION, CriterionName.NOISE))
    print('Electric Engine > Diesel Engine : {}'.format(argument_model.A1.preference.is_preferred_item(*argument_model.item_list)))
    print('Electric Engine (for agent 1) = {}'.format(argument_model.item_list[1].get_score(argument_model.A1.preference)))
    print('Diesel Engine (for agent 1) = {}'.format(argument_model.item_list[0].get_score(argument_model.A1.preference)))
    print('Most preferred item is : {}'.format(argument_model.A1.preference.most_preferred(argument_model.item_list).get_name()))
    print('Diesel Engine among top 10 items : {}'.format(argument_model.A1.preference.is_item_among_top_10_percent(argument_model.item_list[0], argument_model.item_list)))


    # To be completed
