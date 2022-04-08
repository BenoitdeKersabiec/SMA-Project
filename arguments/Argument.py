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

    def __init__(self, boolean_decision, item, preference):
        """Creates a new Argument.
        """
        self.__decision = boolean_decision
        self.__item = item.get_name()
        self.__comparison_list = []
        self.__couple_values_list = []
        self.__positiveCriterionValues = [Value.VERY_GOOD, Value.GOOD]
        self.__negativeCriterionValues = [Value.VERY_BAD, Value.BAD]
        self.__preference = preference

    def add_premiss_comparison(self, criterion_name_1, criterion_name_2):
        """Adds a premiss comparison in the comparison list.
        """
        self.__comparison_list.append(Comparison(criterion_name_1, criterion_name_2))

    def add_premiss_couple_values(self, criterion_name, value):
        """Add a premiss couple values in the couple values list.
        """
        self.__couple_values_list.append(CoupleValue(criterion_name, value))

    def get_comparison_list(self):
        return self.__comparison_list
    
    def get_couple_values_list(self):
        return self.__couple_values_list

    def get_decision(self):
        return self.__decision

    def create_arguments(self):
        criterions = self.__preference.get_criterion_name_list()
        for i in range(len(criterions)-1):
            for j in range(i+1, len(criterions)):
                self.add_premiss_comparison(criterions[i], criterions[j])
        for crit in criterions:    
            value = self.__preference.get_value(self.__item, crit)
            if self.__decision and value in self.__positiveCriterionValues:
                self.add_premiss_couple_values(crit, value)
            if not self.__decision and value in self.__negativeCriterionValues:
                self.add_premiss_couple_values(crit, value)
        



    