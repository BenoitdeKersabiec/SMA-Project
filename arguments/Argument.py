#!/usr/bin/env python3

from arguments.Comparison import Comparison
from arguments.CoupleValue import CoupleValue
from communication.preferences.Value import Value
from communication.preferences.CriterionName import CriterionName
from communication.preferences.Preferences import Preferences


class Argument:
    """Argument class.
    This class implements an argument used in the negotiation.

    attr:
        decision:
        item:
        comparison_list:
        couple_values_list:
    """

    def __init__(self, boolean_decision, item):
        """Creates a new Argument.
        """
        self.__decision = boolean_decision
        self.__item = item.get_name()
        self.__comparison_list = []
        self.__couple_values_list = []
        self.__positiveCriterionValues = [Value.VERY_GOOD, Value.GOOD]
        self.__negativeCriterionValues = [Value.VERY_BAD, Value.BAD]

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premiss comparison in the comparison list.
        """
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    def List_supporting_proposal(self, item, preferences):
        """Generates a list of premisses which can be used to support an item 
        :param item: Item - name of the item
        :return: list of all premisses PRO an item (sorted by order of importance
        based on agent’s preferences) """
        supportingCriterion = []
        for criterion in preferences.get_criterion_name_list():
            if preferences.get_value(item, criterion) in self.__positiveCriterionValues:
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
            if preferences.get_value(item, criterion) in self.__negativeCriterionValues:
                attackingCriterion.append(criterion)
        return attackingCriterion

    