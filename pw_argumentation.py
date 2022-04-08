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
        # for in_message in inbox:
        #     if in_message.get_performative().name == "PROPOSE":
        #         if self.preference.is_item_among_top_10_percent(received[-1].get_content(), self.model.item_list):
        #             out_respond = Message(self.get_name(), in_message.get_exp(), MessagePerformative(102), in_message.get_content())
        #             print(self.get_name(), "sending message:")
        #             print(out_respond)
        #             self.send_message(out_respond)
        #             self.state="Accepted"
        #         else:
        #             out_respond = Message(self.get_name(), in_message.get_exp(), MessagePerformative(104), in_message.get_content())
        #             print(out_respond)
        #             self.send_message(out_respond)
        #     if in_message.get_performative().name == "COMMIT" and self.state == "Accepted":
        #         out_respond = Message(self.get_name(), in_message.get_exp(), MessagePerformative(103), in_message.get_content())
        #         print(out_respond)
        #         self.send_message(out_respond)
        for received in inbox:
            print(received)
            exp = received.get_exp()
            perf = received.get_performative()
            item = received.get_content()
            if perf==MessagePerformative.PROPOSE:
                if self.preference.is_item_among_top_10_percent(item, self.model.item_list):
                    respond = Message(self.get_name(), exp, MessagePerformative.ACCEPT, item)
                    self.send_message(respond)
                else:
                    respond = Message(self.get_name(), exp, MessagePerformative.ASK_WHY, item)
                    self.send_message(respond)
            elif perf==MessagePerformative.ACCEPT:
                respond = Message(self.get_name(), exp, MessagePerformative.COMMIT, item)
                self.send_message(respond)
            elif perf==MessagePerformative.COMMIT:
                previous_messages = self.get_messages_from_exp(exp)
                if len(previous_messages)>1 and previous_messages[-2].get_performative()==MessagePerformative.ACCEPT and item not in self.model.accepted_items:
                    self.model.accepted_items.append(item)
                else:
                    respond = Message(self.get_name(), exp, MessagePerformative.COMMIT, item)
                    self.send_message(respond)
            elif perf==MessagePerformative.ASK_WHY:
                arg = self.support_proposal(item)
                print(arg)
                respond = Message(self.get_name(), exp, MessagePerformative.ARGUE, item)
                self.send_message(respond)




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

    def support_proposal(self, item): 
        """  
        Used when the agent receives "ASK_WHY" after having proposed an item 
        :param item: str- name of the item which was proposed 
        :return: string- the strongest supportive argument 
        """
        argument = Argument(boolean_decision=True, item=item)
        list_supporting_proposal = argument.List_supporting_proposal(item=item, preferences = self.get_preference())
        if len(list_supporting_proposal) == 0:
            print("No argument to support the item")
            best_argument = None
        else:
            best_argument = list_supporting_proposal[0]
        return best_argument

    def argument_parsing (self , argument):
        """ 
        Returns parsed arguments
        :param argument:
        :return tuple:
        """
        return (argument.get_decision(), argument.get_comparison_list(),argument.get_couple_values_list())

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
    agents = argument_model.schedule.agents
    agent1, agent2 = agents[0], agents[1]
    message = Message(agent1.get_name(), agent2.get_name(), MessagePerformative.PROPOSE, argument_model.item_list[1])
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
    steps=20
    while steps>0:
        steps-=1
        for agent in argument_model.schedule.agents:
            agent.step()

    

