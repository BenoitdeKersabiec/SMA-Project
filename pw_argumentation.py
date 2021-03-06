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
from arguments.Argument import Argument
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
        inbox = self.get_new_messages()
        for received in inbox:
            print(received)
            exp = received.get_exp()
            perf = received.get_performative()
            item = received.get_content()
            if perf == MessagePerformative.PROPOSE:
                if self.preference.is_item_among_top_10_percent(item, self.model.item_list):
                    respond = Message(self.get_name(), exp, MessagePerformative.ACCEPT, item)
                    self.send_message(respond)
                else:
                    respond = Message(self.get_name(), exp, MessagePerformative.ASK_WHY, item)
                    self.send_message(respond)
            elif perf == MessagePerformative.ACCEPT:
                respond = Message(self.get_name(), exp, MessagePerformative.COMMIT, item)
                self.send_message(respond)
            elif perf == MessagePerformative.COMMIT:
                previous_messages = self.get_messages_from_exp(exp)
                if len(previous_messages) > 1 and previous_messages[
                    -2].get_performative() == MessagePerformative.ACCEPT and item not in self.model.accepted_items:
                    self.model.accepted_items.append(item)
                else:
                    respond = Message(self.get_name(), exp, MessagePerformative.COMMIT, item)
                    self.send_message(respond)
            elif perf == MessagePerformative.ASK_WHY:
                arg = self.support_proposal(item)
                # print(arg)
                respond = Message(self.get_name(), exp, MessagePerformative.ARGUE, arg)

                self.send_message(respond)
            elif perf == MessagePerformative.ARGUE:
                if self.can_be_attacked_or_not(item):
                    pass
                else:
                    respond = Message(self.get_name(), exp, MessagePerformative.ACCEPT, item)
                    self.send_message(respond)

    def get_preference(self):
        return self.preference

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

    def support_proposal(self, item):
        """  
        Used when the agent receives "ASK_WHY" after having proposed an item 
        :param item: str- name of the item which was proposed 
        :return: string- the strongest supportive argument 
        """
        argument = Argument(boolean_decision=True, item=item, preference=self.get_preference())
        list_supporting_proposal = self.List_supporting_proposal(item=item, preferences=self.get_preference())
        if len(list_supporting_proposal) == 0:
            print("No argument to support the item")
            best_argument = None
        else:
            argument.create_arguments()
            best_argument = argument.get_couple_values_list()[0]
            
        return best_argument

    def List_supporting_proposal(self, item, preferences):
        """Generates a list of premisses which can be used to support an item 
        :param item: Item - name of the item
        :return: list of all premisses PRO an item (sorted by order of importance
        based on agent???s preferences) """
        supportingCriterion = []
        for criterion in preferences.get_criterion_name_list():
            if preferences.get_value(item, criterion) in [Value.VERY_GOOD, Value.GOOD]:
                supportingCriterion.append(criterion)
        print(f"preferences.get_criterion_name_list() = {preferences.get_criterion_name_list()}")
        print(f"supportingCriterion = {supportingCriterion}")
        return supportingCriterion

    def List_attacking_proposal(self, item, preferences):
        """Generates a list of premisses which can be used to attack an item 
        :param item: Item - name of the item
        :return: list of all premisses CON an item (sorted by order of importance
        based on preferences) """
        attackingCriterion = []
        for criterion in preferences.get_criterion_name_list():
            if preferences.get_value(item, criterion) in [Value.VERY_BAD, Value.BAD]:
                attackingCriterion.append(criterion)
        return attackingCriterion

    def argument_parsing(self, argument):
        return argument.get_comparison_list(), argument.get_couple_values_list(), argument.get_decision()

    def can_be_attacked_or_not(self, argument):
        comparisons, couples_values, decisions = self.argument_parsing(argument)
        pref = self.get_preference()
        criterions_ordered = pref.get_criterions_name_list()
        item = argument.__item


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
        self.accepted_items = []

        self.A1 = ArgumentAgent(1, self, 'Alice', Preferences())
        self.A2 = ArgumentAgent(2, self, 'Bob', Preferences())

        # Random
        # self.A1.generate_preferences(self.item_list)
        # self.A2.generate_preferences(self.item_list)

        #Example of the subject
        crit_names = list(CriterionName)
        self.A1.preference.set_criterion_name_list([crit_names[0], crit_names[3], crit_names[1], crit_names[2], crit_names[4]])
        self.A2.preference.set_criterion_name_list([crit_names[3], crit_names[4], crit_names[0], crit_names[1], crit_names[2]])

        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[0], Value.GOOD))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[1], Value.AVERAGE))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[2], Value.GOOD))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[3], Value.VERY_BAD))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[4], Value.BAD))

        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[0], Value.AVERAGE))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[1], Value.BAD))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[2], Value.AVERAGE))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[3], Value.VERY_BAD))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[0], crit_names[4], Value.VERY_BAD))

        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[0], Value.BAD))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[1], Value.VERY_BAD))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[2], Value.AVERAGE))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[3], Value.GOOD))
        self.A1.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[4], Value.GOOD))

        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[0], Value.AVERAGE))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[1], Value.BAD))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[2], Value.BAD))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[3], Value.GOOD))
        self.A2.preference.add_criterion_value(CriterionValue(self.item_list[1], crit_names[4], Value.GOOD))

        self.schedule.add(self.A1)
        self.schedule.add(self.A2)
        self.running = True

    def step(self):
        self.__messages_service.dispatch_messages(self.A1, self.A2, )
        self.schedule.step()


if __name__ == "__main__":
    argument_model = ArgumentModel()
    agents = argument_model.schedule.agents
    agent1, agent2 = agents[0], agents[1]

    message = Message(agent1.get_name(), agent2.get_name(), MessagePerformative.PROPOSE, argument_model.item_list[0])
    agent1.send_message(message)
    # print(message)
    # argument_model.A1.send_message(message)
    # received = argument_model.A2.get_new_messages()
    # if argument_model.A2.preference.is_item_among_top_10_percent(received[-1].get_content(), argument_model.item_list):
    #     respond = Message("Bob", "Alice", MessagePerformative.ACCEPT, received[-1].get_content())
    #     print(respond)
    #     argument_model.A2.send_message(respond)
    #     argument_model.A1.send_message(Message("Bob", "Alice", MessagePerformative.COMMIT, received[-1].get_content()))
    #     argument_model.A2.send_message(Message("Bob", "Alice", MessagePerformative.COMMIT, received[-1].get_content()))
    # else:
    #     respond = Message("Bob", "Alice", MessagePerformative.ASK_WHY, received[-1].get_content())
    #     print(respond)
    #     argument_model.A2.send_message(respond)
    steps = 20
    while steps > 0:
        steps -= 1
        for agent in argument_model.schedule.agents:
            agent.step()
