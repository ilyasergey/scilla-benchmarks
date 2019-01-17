import utils
from utils import ContractFunction, get_addresses, get_random_address,\
    get_random_number, addresses


SENDER_ADDRESS = '0xfaB8FcF1b5fF9547821B4506Fa0C35c68a555F90'
SENDER_PRIVKEY = '4bc95d997c4c700bb4769678fa8452c2f67c9348e33f6f32b824253ae29a5316'
total_token_supply = 1000000 * 10**16

TRANSACTION_LIMIT = 10
TEST_ITERATIONS = 10

contracts_benchmark_plans = [
    # {
    #    'contract_filename': 'add.sol',
    #    'contract_name': 'Addition',
    #    'constructor': (),
    #    'transactions': [
    #        ('add(int256,int256)', 4, 5)
    #    ]
    # },
    {
        'contract_filename': 'fungible-token.sol',
        'contract_name': 'TokenERC20',
        'constructor': (
            ('uint256', 'string', 'string'),
            (total_token_supply, 'Test', 'TEST')),
        'transactions': [
            {
                'function':  ContractFunction('transfer', ('address', 'uint256')),
                'values': (addr, 1*(10**16)),
                'caller': SENDER_ADDRESS,
            }
            for addr in addresses[:TRANSACTION_LIMIT]
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
            (TRANSACTION_LIMIT*10,)
            # ('uint256', 'string', 'string'),
            # (total_token_supply, 'Test', 'TEST'),
        ),
        'transactions': [
            {
                'function': ContractFunction('safeTransferFrom',
                                             ('address', 'address', 'uint256')),
                'values': (SENDER_ADDRESS, addr, index),
                'caller': SENDER_ADDRESS
            }
            for index, addr in enumerate(addresses[:TRANSACTION_LIMIT])
        ],
        'tests': [
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
            {
                'test_name': 'approve',
                'transactions': [
                    {
                        'function': ContractFunction(
                            'approve', ('address', 'uint256')),
                        'values': (SENDER_ADDRESS, utils.get_random_token_id),
                        'caller': SENDER_ADDRESS
                    }
                    for iteration in range(TEST_ITERATIONS)
                ]
            }

        ]
    },
    {
        'contract_filename': 'crowdfunding.sol',
        'contract_name': 'Crowdfunding',
        'constructor': (
            ('uint256', 'uint256'),
            (1, 100)
        ),
        'transactions': [
            {
                'function': ContractFunction('pledge', ('uint256',)),
                'values': (1,),
                'caller': addr
            }
            for addr in addresses[:TRANSACTION_LIMIT]
        ],
        'tests': [

            {
                'test_name': 'pledge',
                'transactions': [
                    {
                        'function': ContractFunction('pledge', ('uint256',)),
                        'values': (1,),
                        'caller': addr,
                    }
                    for addr in addresses[:TEST_ITERATIONS]
                ]
            },

            {
                'test_name': 'approve',
                'setup_transactions': [
                    {
                        'function': ContractFunction('pledge', ('uint256',)),
                        'values': (1,),
                        'caller': addr,
                    }
                    for addr in addresses[:TEST_ITERATIONS]
                ],
                'transactions': [
                    {
                        'function': ContractFunction('claimFunds', ()),
                        'values': (),
                        'caller': addr,
                    }
                    for addr in addresses[:TEST_ITERATIONS]
                ]
            },

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
