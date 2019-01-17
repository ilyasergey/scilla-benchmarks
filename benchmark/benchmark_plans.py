import utils
from utils import ContractFunction, get_addresses, get_random_address,\
    use_address, get_random_number


SENDER_ADDRESS = '0xfaB8FcF1b5fF9547821B4506Fa0C35c68a555F90'
SENDER_PRIVKEY = '4bc95d997c4c700bb4769678fa8452c2f67c9348e33f6f32b824253ae29a5316'
total_token_supply = 1000000 * 10**16

TRANSACTION_LIMIT = 10
TEST_ITERATIONS = 100

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
    #     'transactions_limit': TRANSACTION_LIMIT,
    #     'transactions': [
    #         (
    #             ContractFunction('transfer', ('address', 'uint256')),
    #             addr, 1*(10**16)
    #         )
    #         for addr in get_addresses()
    #     ],
    #     'tests': [
    #         {
    #             'function': ContractFunction(
    #                 'transfer', ('address', 'uint256')),
    #             'values': (get_random_address, get_random_number),
    #             'iterations': TEST_ITERATIONS
    #         },
    #         {
    #             'function': ContractFunction(
    #                 'approve', ('address', 'uint256')),
    #             'values': (get_random_address, get_random_number),
    #             'iterations': TEST_ITERATIONS
    #         },
    #     ]
    # },
    {
        'contract_filename': 'non-fungible-token.sol',
        'contract_name': 'ERC721',
        'constructor': (
            ('uint256',),
            (TRANSACTION_LIMIT*10,)
            # ('uint256', 'string', 'string'),
            # (total_token_supply, 'Test', 'TEST'),
        ),
        'transactions_limit': TRANSACTION_LIMIT,
        'transactions': [
            (
                ContractFunction('safeTransferFrom',
                                 ('address', 'address', 'uint256')),
                SENDER_ADDRESS, addr, index
            )
            for index, addr in enumerate(get_addresses())
        ],
        'tests': [
            {
                'function': ContractFunction(
                    'safeTransferFrom', ('address', 'address', 'uint256')),
                'values': (use_address(SENDER_ADDRESS), get_random_address, utils.get_random_token_id),
                'iterations': TEST_ITERATIONS
            },
            {
                'function': ContractFunction(
                    'approve', ('address', 'uint256')),
                'values': (use_address(SENDER_ADDRESS), utils.get_random_token_id),
                'iterations': TEST_ITERATIONS
            },
        ]
    },

]
