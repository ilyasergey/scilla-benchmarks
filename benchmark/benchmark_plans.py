from utils import ContractFunction, get_addresses


SENDER_ADDRESS = '0xfaB8FcF1b5fF9547821B4506Fa0C35c68a555F90'
SENDER_PRIVKEY = '4bc95d997c4c700bb4769678fa8452c2f67c9348e33f6f32b824253ae29a5316'
total_token_supply = 1000000 * 10**16

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
    #     'transactions_limit': 1000,
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
    #             'iterations': 100
    #         },
    #         {
    #             'function': ContractFunction(
    #                 'approve', ('address', 'uint256')),
    #             'iterations': 100
    #         },
    #     ]
    # },
    {
        'contract_filename': 'non-fungible-token.sol',
        'contract_name': 'ERC721',
        'constructor': (
            ('uint256', 'string', 'string'),
            (total_token_supply, 'Test', 'TEST')),
        'transactions_limit': 10,
        'transactions': [
            (
                ContractFunction('safeTransferFrom',
                                 ('address', 'address', 'uint256')),
                SENDER_ADDRESS, addr, 1*(10**16)
            )
            for addr in get_addresses()
        ],
        # 'tests': [
        #     {
        #         'function': ContractFunction(
        #             'safeTransferFrom', ('address', 'address', 'uint256')),
        #         'iterations': 100
        #     },
        #     #     {
        #     #         'function': ContractFunction(
        #     #             'approve', ('address', 'uint256')),
        #     #         'iterations': 100
        #     #     },
        # ]
    },

]
