import sys
import random
import utils
from utils import ContractFunction, get_addresses, get_random_address,\
    get_random_number, addresses, SENDER_ADDRESS
from evm_tools import perform_transaction


total_token_supply = 1000000 * 10**16

TRANSACTION_LIMIT = int(sys.argv[1])

TEST_ITERATIONS = 100

if len(sys.argv) > 2:
    TEST_ITERATIONS = int(sys.argv[2])


print('Using {:,} state entries'.format(TRANSACTION_LIMIT))

contracts_benchmark_plans = [
    {
        'contract_filename': 'fungible-token.sol',
        'contract_name': 'ERC20',
        'constructor': (
            # ('uint256', 'string', 'string'),
            # (total_token_supply, 'Test', 'TEST'),
            ('uint256', 'string', 'string', 'address[]'),
            (total_token_supply, 'Test', 'TEST',
             addresses[:TRANSACTION_LIMIT]),
        ),
        'transactions': [
            # {
            #     'function':  ContractFunction('transfer', ('address', 'uint256', 'address[]')),
            #     'values': (addr, 1*(10**16), addresses),
            #     'caller': SENDER_ADDRESS,
            # }
            # for addr in addresses[:TRANSACTION_LIMIT]
        ],
        'tests': [
            {
                'test_name': 'transfer',
                'transactions': [
                    {
                        'function': ContractFunction(
                            'transfer', ('address', 'uint256')),
                        'values': (get_random_address, get_random_number),
                        'caller': SENDER_ADDRESS
                    }
                    for iteration in range(TEST_ITERATIONS)
                ]
            },
            {
                'test_name': 'approve',
                'transactions': [
                    {
                        'function': ContractFunction(
                            'approve', ('address', 'uint256')),
                        'caller': SENDER_ADDRESS,
                        'values': (get_random_address, get_random_number),
                    }
                    for iteration in range(TEST_ITERATIONS)
                ]
            }

        ]
    },
    {
        'contract_filename': 'non-fungible-token.sol',
        'contract_name': 'ERC721',
        'constructor': (
            ('uint256',),
            (TRANSACTION_LIMIT,)
            # ('uint256', 'string', 'string'),
            # (total_token_supply, 'Test', 'TEST'),
        ),
        'transactions': [
            # {
            #     'function': ContractFunction('safeTransferFrom',
            #                                  ('address', 'address', 'uint256')),
            #     'values': (SENDER_ADDRESS, addr, index),
            #     'caller': SENDER_ADDRESS
            # }
            # for index, addr in enumerate(addresses[:TRANSACTION_LIMIT])
        ],
        'tests': [
            {
                'test_name': 'setApprovalForAll',
                'transactions': [
                    {
                        'function': ContractFunction(
                            'setApprovalForAll', ('address', 'uint256')),
                        'values': (get_random_address, utils.get_random_token_id),
                        'caller': SENDER_ADDRESS,
                    }
                    for iteration in range(TEST_ITERATIONS)
                ]
            },
            {
                'test_name': 'safeTransferFrom',
                'transactions': [
                    {
                        'function': ContractFunction(
                            'safeTransferFrom', ('address', 'address', 'uint256')),
                        'values': (SENDER_ADDRESS, get_random_address, utils.get_random_token_id),
                        'caller': SENDER_ADDRESS,
                    }
                    for iteration in range(TEST_ITERATIONS)
                ]
            },
            # {
            #     'test_name': 'approve',
            #     'transactions': [
            #         {
            #             'function': ContractFunction(
            #                 'approve', ('address', 'uint256')),
            #             'values': (SENDER_ADDRESS, utils.get_random_token_id),
            #             'caller': SENDER_ADDRESS
            #         }
            #         for iteration in range(TEST_ITERATIONS)
            #     ]
            # }

        ]
    },

    {
        'contract_filename': 'auction.sol',
        'contract_name': 'SimpleAuction',
        'constructor': (
            ('uint256', 'address', 'address[]'),
            (1000, SENDER_ADDRESS, addresses[:TRANSACTION_LIMIT])
        ),
        'transactions': [
            # {
            #     'function': ContractFunction('bid', ()),
            #     'values': (),
            #     'amount': 1*index,
            #     'caller': addr
            # }
            # for index, addr in enumerate(addresses[:TRANSACTION_LIMIT])
        ],
        'tests': [

            {
                # increment the bid each iteration
                # so we can do the withdraw function for the losers
                # there can only be 1 winning bid, so the total number of bids is n+1
                'test_name': 'bid',
                'transactions': [
                    {
                        'function': ContractFunction('bid', ()),
                        'values': (),
                        'amount': 1000*index,
                        'caller': addr,
                    }
                    for index, addr in enumerate(addresses[:TEST_ITERATIONS])
                ]
            },

            {
                'test_name': 'withdraw',
                'transactions': [
                    {
                        'function': ContractFunction('withdraw', ()),
                        'values': (),
                        'caller': addr,
                    }
                    for index, addr in enumerate(addresses[:TEST_ITERATIONS])
                ]
            },
        ]
    },

    {
        'contract_filename': 'crowdfunding.sol',
        'contract_name': 'Crowdfunding',
        'constructor': (
            ('uint256', 'uint256', 'address[]'),
            (1, 1000, addresses[:TRANSACTION_LIMIT]),
        ),
        'transactions': [
            # {
            #     'function': ContractFunction('pledge', ('uint256',)),
            #     'values': (1,),
            #     'caller': addr,
            #     'amount': 1
            # }
            # for addr in addresses[:TRANSACTION_LIMIT]
        ],
        'tests': [
            {
                'test_name': 'pledge',
                'transactions': [
                    {
                        'function': ContractFunction('pledge', ('uint256',)),
                        'values': (100,),
                        'caller': addr,
                        'amount': 1
                    }
                    for addr in addresses[:TEST_ITERATIONS]
                ]
            },

            # {
            #     'test_name': 'claimFunds',
            #     'transactions': [
            #         {
            #             'function': ContractFunction('claimFunds', ()),
            #             'values': (),
            #             'caller': SENDER_ADDRESS,
            #             'amount': 0
            #         }
            #         for addr in addresses[:TEST_ITERATIONS]
            #     ]
            # },

            {
                'test_name': 'getRefund',
                'transactions': [
                    {
                        'function': ContractFunction('getRefund', ()),
                        'values': (),
                        'caller': addr,
                        'time': 9547698860
                    }
                    for addr in addresses[:TEST_ITERATIONS]
                ]
            },
        ]
    },

]
