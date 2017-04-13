#!/usr/bin/env python
"""Parse module defines a parse class and defines contract and check file specifications"""

from src.contract import Contract
from src.check import Check
from src.check import Checks

# contract file attributes
TAB_WIDTH = 2
COMMENT_CHAR = '##'
CONTRACT_HEADER = 'CONTRACT:'
CONTRACT_NAME_HEADER = 'NAME:'
CONTRACT_VARIABLES_HEADER = 'VARIABLES:'
CONTRACT_ASSUMPTIONS_HEADER = 'ASSUMPTIONS:'
CONTRACT_GUARANTEES_HEADER = 'GUARANTEES:'
CHECKS_HEADER = 'CHECKS:'


def parse(infile):
    """Parses input text file

    Returns:
            A tuple of a list of contracts and a list of checks

    """
    # init return variables
    contracts, checks = {}, None

    with open(infile, 'r') as in_file:

        for line in in_file:
            line = __clean_line(line)

            # skip empty lines
            if not line.strip():
                continue

            # parse contract
            if CONTRACT_HEADER in line:
                tab_lim = __line_indentation(line)
                contract = __parse_contract(tab_lim, in_file)
                contracts[contract.name] = contract

            # parse checks
            if CHECKS_HEADER in line:
                tab_lim = __line_indentation(line)
                checks = __parse_checks(tab_lim, in_file, contracts)

    return contracts, checks

def compile(contracts, checks):

    # generate output file
    outfile = open('nusmv.smv', 'w')
    outfile.write("MODULE main\n")

    # Iterate through the contracts dictionary, breaking after printing the variables from the first contract
    # (because for now, all contracts have the same variables)
    # TEMP -> Change for alphabet projection
    outfile.write("VAR\n")
    for k, v in contracts.items():
        for var in v.variables:
            var_char = var[:(var.find(":="))]
            outfile.write("\t" + var_char + ": boolean;\n")
        break

    # Iterate through the contracts dictionary, breaking after initializing the values of the variables
    # from the first contract
    outfile.write("ASSIGN\n")
    for k, v in contracts.items():
        for var in v.variables:
            idx = var.find(" :=")
            var_char = var[:idx]
            outfile.write("\tinit(" + var_char + ")" + var[idx:] + ";\n")
        break

    # -- END TEMP -- 

    outfile.write("\n")

    # Cleanup the Contracts to concatenate assumptions and guarantees and put into saturated form
    for k,v in contracts.items():
        v.cleanup_contract()
        # print "\n", v

    # Iterate through all checks and run the corresponding function for that test (for now, only works with 2 contracts)
    for check in checks:
        if check.check_type == 'compatibility': 
            comp = self.compatibility(contracts[check.contract_names[0]],contracts[check.contract_names[1]])
            outfile.write(comp)

                # Uncomment the line below if you want to test the correctness of the composition function)
                # self.composition(contracts[check.contract_names[0]],contracts[check.contract_names[1]])

                # Uncomment the line below if you want to test the correctness of the conjunction function)
                # self.conjunction(contracts[check.contract_names[0]],contracts[check.contract_names[1]])
        elif check.check_type == 'consistency': 
            const = self.consistency(contracts[check.contract_names[0]],contracts[check.contract_names[1]])
            outfile.write(const)

    # Return the name of the generated .smv file so the calling function can run NuSMV
    return 'nusmv.smv'

def __parse_contract(tab_lim, afile):
    """Parses a contract block within the input text file"""
    contract = Contract() # init contract object
    group = None # init group variable

    # init array for contract data and contract data adder utility functions
    data = [
        ('name', CONTRACT_NAME_HEADER, contract.set_name, []),
        ('variables', CONTRACT_VARIABLES_HEADER, contract.set_variables, []),
        ('assumptions', CONTRACT_ASSUMPTIONS_HEADER, contract.set_assumptions, []),
        ('guarantees', CONTRACT_GUARANTEES_HEADER, contract.set_guarantees, [])
    ]

    # parse contract
    for line in afile:
        line = __clean_line(line)
        tab_len = __line_indentation(line)

        # end parse when number of indents is lower than or equal to tab limit
        if tab_len <= tab_lim:
            break

        # when number of indents is one more than limit, parce header
        elif tab_len == tab_lim + 1:
            group = [x for x in data if x[1] in line][0]

        # when number of indents is more than header, parce data
        else:
            group[3].append(line.strip())

    # add contract elements to contract object
    data = [x[2](x[3]) for x in data]

    return contract

def __parse_checks(tab_lim, afile, contracts):
    """Parses the checks block within the input text file"""
    checks = Checks()

    # parse checks
    for line in afile:
        line = __clean_line(line)
        tab_len = __line_indentation(line)

        # end parse when number of indents is lower than or equal to tab limit
        if tab_len <= tab_lim:
            break

        # when number of indents is greater than tab limit
        else:
            # parse check
            check_type, check_contracts = line.split('(', 1)

            # find contracts associated with check
            check_contracts = check_contracts[:-1].split(',')
            check_contracts = [contracts[x.strip()] for x in check_contracts]

            # construct and store check
            check = Check()
            check.set_type(check_type.strip())
            check.set_contracts(check_contracts)
            checks.add_check(check)

    return checks

def __clean_line(cls, line):
    """Returns a comment-free, tab-replaced line with no ending whitespace"""
    line = line.split(COMMENT_CHAR, 1)[0] # remove comments
    line = line.replace('\t', ' ' * TAB_WIDTH) # replace tabs with spaces
    return line.rstrip() # remove ending whitespace

def __line_indentation(cls, line):
    """Returns the number of indents on a given line"""
    return (len(line) - len(line.lstrip(' '))) / TAB_WIDTH
