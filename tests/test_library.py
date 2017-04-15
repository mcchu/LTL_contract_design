#!/usr/bin/env python
"""Test Library module provides a test suite for LTL contract verifier"""

import os
import sys
import unittest
from src.core import parse, generate, run
from src.contract import Contract, Contracts
from src.check import Compatibility, Consistency, Checks

sys.path.append(os.path.join(os.getcwd(), os.path.pardir))


class TestLibrary(unittest.TestCase):
    """TestLibrary class contains method to test LTL contract verifier operations"""

    def test_waiter_customer_model(self):
        """Parse waiter customer model and verify returned contracts and checks objects"""

        # parse waiter customer model
        contracts, checks = parse('tests/waiter_customer.txt')

        # verify waiter contract parsed correctly
        waiter = Contract()
        waiter.set_name(['waiter'])
        waiter.set_variables([('request', 'FALSE'), ('service', 'FALSE')])
        waiter.set_assumptions(['TRUE'])
        waiter.set_guarantees(
            ['G(!request -> X !service)', 'G(request -> X service)'])
        self.assertEqual(contracts.get_contract('waiter'), waiter)

        # verify customer contract parsed correctly
        customer = Contract()
        customer.set_name(['customer'])
        customer.set_variables([('request', 'FALSE'), ('service', 'FALSE')])
        customer.set_assumptions(['TRUE'])
        customer.set_guarantees(['(F request)', 'G((request & !service) -> X request)',
                                 'G(service -> X !request)'])
        self.assertEqual(contracts.get_contract('customer'), customer)

        # verify all contracts have been parsed
        test_contracts = Contracts()
        test_contracts.add_contract(waiter)
        test_contracts.add_contract(customer)
        self.assertEqual(test_contracts, contracts)

        # verify compatibility check
        compatibility = Compatibility()
        compatibility.set_contracts([waiter, customer])
        self.assertEqual(compatibility, checks.checks[0])

        # verify consistency check
        consistency = Consistency()
        consistency.set_contracts([waiter, customer])
        self.assertEqual(consistency, checks.checks[1])

        # verify all checks have been parsed correctly
        test_checks = Checks()
        test_checks.add_check(compatibility)
        test_checks.add_check(consistency)
        self.assertEqual(test_checks, checks)

    def test_checks(self):
        """Runs the program and outputs status of the LTL statements"""

        # parse waiter customer model
        contracts, checks = parse('tests/waiter_customer.txt')
        #run(cont)
