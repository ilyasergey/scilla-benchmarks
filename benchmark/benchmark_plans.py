import utils
from utils import ContractFunction, get_addresses, get_random_address,\
    get_random_number, addresses, SENDER_ADDRESS
from evm_tools import deploy_etheremon_database_contract


total_token_supply = 1000000 * 10**16

TRANSACTION_LIMIT = 10
TEST_ITERATIONS = 100

CROWDFUNDING_GOAL = 100

# each pledge must exceed the
pledge_transactions = [
    {
        'function': ContractFunction('pledge', ('uint256',)),
        'values': (CROWDFUNDING_GOAL+1,),
        'caller': addr,
        'amount': CROWDFUNDING_GOAL+1
    }
    for addr in addresses[:TEST_ITERATIONS]
]
claim_funds_transactions = [
    {
        'function': ContractFunction('claimFunds', ()),
        'values': (),
        'caller': SENDER_ADDRESS,
    }
    for iteration in range(TEST_ITERATIONS)
]
interleaved_transactions = pledge_transactions + claim_funds_transactions
interleaved_transactions[::2] = pledge_transactions
interleaved_transactions[1::2] = claim_funds_transactions

contracts_benchmark_plans = [
    # {
    #    'contract_filename': 'add.sol',
    #    'contract_name': 'Addition',
    #    'constructor': (),
    #    'transactions': [
    #        ('add(int256,int256)', 4, 5)
    #    ]
    # },
    # {
    #     'contract_filename': 'fungible-token.sol',
    #     'contract_name': 'TokenERC20',
    #     'constructor': (
    #         ('uint256', 'string', 'string'),
    #         (total_token_supply, 'Test', 'TEST')),
    #     'transactions': [
    #         {
    #             'function':  ContractFunction('transfer', ('address', 'uint256')),
    #             'values': (addr, 1*(10**16)),
    #             'caller': SENDER_ADDRESS,
    #         }
    #         for addr in addresses[:TRANSACTION_LIMIT]
    #     ],
    #     'tests': [
    #         {
    #             'test_name': 'transfer',
    #             'transactions': [
    #                 {
    #                     'function': ContractFunction(
    #                         'transfer', ('address', 'uint256')),
    #                     'values': (get_random_address, get_random_number),
    #                     'caller': SENDER_ADDRESS
    #                 }
    #                 for iteration in range(TEST_ITERATIONS)
    #             ]
    #         },
    #         {
    #             'test_name': 'approve',
    #             'transactions': [
    #                 {
    #                     'function': ContractFunction(
    #                         'approve', ('address', 'uint256')),
    #                     'caller': SENDER_ADDRESS,
    #                     'values': (get_random_address, get_random_number),
    #                 }
    #                 for iteration in range(TEST_ITERATIONS)
    #             ]
    #         }

    #     ]
    # },
    # {
    #     'contract_filename': 'non-fungible-token.sol',
    #     'contract_name': 'ERC721',
    #     'constructor': (
    #         ('uint256',),
    #         (TRANSACTION_LIMIT*10,)
    #         # ('uint256', 'string', 'string'),
    #         # (total_token_supply, 'Test', 'TEST'),
    #     ),
    #     'transactions': [
    #         {
    #             'function': ContractFunction('safeTransferFrom',
    #                                          ('address', 'address', 'uint256')),
    #             'values': (SENDER_ADDRESS, addr, index),
    #             'caller': SENDER_ADDRESS
    #         }
    #         for index, addr in enumerate(addresses[:TRANSACTION_LIMIT])
    #     ],
    #     'tests': [
    #         {
    #             'test_name': 'safeTransferFrom',
    #             'transactions': [
    #                 {
    #                     'function': ContractFunction(
    #                         'safeTransferFrom', ('address', 'address', 'uint256')),
    #                     'values': (SENDER_ADDRESS, get_random_address, utils.get_random_token_id),
    #                     'caller': SENDER_ADDRESS,
    #                 }
    #                 for iteration in range(TEST_ITERATIONS)
    #             ]
    #         },
    #         {
    #             'test_name': 'approve',
    #             'transactions': [
    #                 {
    #                     'function': ContractFunction(
    #                         'approve', ('address', 'uint256')),
    #                     'values': (SENDER_ADDRESS, utils.get_random_token_id),
    #                     'caller': SENDER_ADDRESS
    #                 }
    #                 for iteration in range(TEST_ITERATIONS)
    #             ]
    #         }

    #     ]
    # },

    # {
    #     'contract_filename': 'auction.sol',
    #     'contract_name': 'SimpleAuction',
    #     'constructor': (
    #         ('uint256', 'address'),
    #         (1000, SENDER_ADDRESS)
    #     ),
    #     'transactions': [
    #         {
    #             'function': ContractFunction('bid', ()),
    #             'values': (),
    #             'amount': 10 * index,
    #             'caller': addr
    #         }
    #         for index, addr in enumerate(addresses[:TRANSACTION_LIMIT])
    #     ],
    #     'tests': [

    # {
    #     'test_name': 'bid',
    #     'transactions': [
    #         {
    #             'function': ContractFunction('bid', ()),
    #             'values': (),
    #             'amount': 10,
    #             'caller': addr,
    #         }
    #         for addr in addresses[:TEST_ITERATIONS]
    #     ]
    # },

    # {
    #     'test_name': 'withdraw',
    #     # increment the bid each iteration
    #     # so we can do the withdraw function for the losers
    #     # there can only be 1 winning bid, so the total number of bids is n+1
    #     'setup_transactions': [
    #         {
    #             'function': ContractFunction('bid', ()),
    #             'values': (),
    #             'amount': index * 10,
    #             'caller': addr,
    #         }
    #         for index, addr in enumerate(addresses[:TEST_ITERATIONS+1])
    #     ],
    #     'transactions': [
    #         {
    #             'function': ContractFunction('withdraw', ()),
    #             'values': (),
    #             'caller': addr,
    #         }
    #         for index, addr in enumerate(addresses[:TEST_ITERATIONS])
    #     ]
    # },

    # {
    #     'test_name': 'getRefund',
    #     'transactions': [
    #         {
    #             'function': ContractFunction('getRefund', ()),
    #             'values': (),
    #             'caller': addr,
    #             'time': 9547698860
    #         }
    #         for addr in addresses[:TEST_ITERATIONS]
    #     ]
    # },
    #     ]
    # },

    # {
    #     'contract_filename': 'crowdfunding.sol',
    #     'contract_name': 'Crowdfunding',
    #     'constructor': (
    #         ('uint256', 'uint256'),
    #         (1, CROWDFUNDING_GOAL)
    #     ),
    #     'transactions': [
    #         {
    #             'function': ContractFunction('pledge', ('uint256',)),
    #             'values': (1,),
    #             'caller': addr,
    #             'amount': 1
    #         }
    #         for addr in addresses[:TRANSACTION_LIMIT]
    #     ],
    #     'tests': [
    #         {
    #             'test_name': 'pledge',
    #             'transactions': [
    #                 {
    #                     'function': ContractFunction('pledge', ('uint256',)),
    #                     'values': (1,),
    #                     'caller': addr,
    #                     'amount': 1
    #                 }
    #                 for addr in addresses[:TEST_ITERATIONS]
    #             ]
    #         },

    #         {
    #             'test_name': 'claimFunds',
    #             'transactions': interleaved_transactions
    #         },

    #         {
    #             'test_name': 'getRefund',
    #             'transactions': [
    #                 {
    #                     'function': ContractFunction('getRefund', ()),
    #                     'values': (),
    #                     'caller': addr,
    #                     'time': 9547698860
    #                 }
    #                 for addr in addresses[:TEST_ITERATIONS]
    #             ]
    #         },
    #     ]
    # },

    # {
    #     'contract_filename': 'etheremon-world.sol',
    #     'contract_name': 'EtheremonWorld',
    #     'constructor': (
    #         ('address',),
    #         (deploy_etheremon_database_contract,)
    #     ),
    #     'transactions': [
    #         {
    #             'function': ContractFunction(
    #                 'addMonsterClassBasic',
    #                 ('uint32', 'uint8', 'uint256', 'uint256',
    #                  'uint8', 'uint8', 'uint8', 'uint8', 'uint8', 'uint8')
    #             ),
    #             'values':  (1, 1, 1, 1,
    #                         1, 1, 1, 1, 1, 1),
    #             'caller': SENDER_ADDRESS
    #         }
    #         for addr in addresses[:TRANSACTION_LIMIT]
    #     ],
    # 'tests': [

    #     {
    #         'test_name': 'bid',
    #         'transactions': [
    #             {
    #                 'function': ContractFunction('bid', ()),
    #                 'values': (),
    #                 'amount': 10,
    #                 'caller': addr,
    #             }
    #             for addr in addresses[:TEST_ITERATIONS]
    #         ]
    #     },

    #     {
    #         'test_name': 'withdraw',
    #         # increment the bid each iteration
    #         # so we can do the withdraw function for the losers
    #         # there can only be 1 winning bid, so the total number of bids is n+1
    #         'setup_transactions': [
    #             {
    #                 'function': ContractFunction('bid', ()),
    #                 'values': (),
    #                 'amount': index * 1,
    #                 'caller': addr,
    #             }
    #             for index, addr in enumerate(addresses[:TEST_ITERATIONS+1])
    #         ],
    #         'transactions': [
    #             {
    #                 'function': ContractFunction('withdraw', ()),
    #                 'values': (),
    #                 'caller': addr,
    #             }
    #             for index, addr in enumerate(addresses[:TEST_ITERATIONS])
    #         ]
    #     },

    #     {
    #         'test_name': 'getRefund',
    #         'transactions': [
    #             {
    #                 'function': ContractFunction('getRefund', ()),
    #                 'values': (),
    #                 'caller': addr,
    #                 'time': 9547698860
    #             }
    #             for addr in addresses[:TEST_ITERATIONS]
    #         ]
    #     },
    # ]
    # },


]
