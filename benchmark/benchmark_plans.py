from utils import ContractFunction, get_addresses


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
    {
        'contract_filename': 'fungible-token.sol',
        'contract_name': 'TokenERC20',
        'constructor': (
            ('uint256', 'string', 'string'),
            (total_token_supply, 'Test', 'TEST')),
        'transactions_limit': 1000,
        'transactions': [
            (
                ContractFunction('transfer', ('address', 'uint256')),
                addr, 1*(10**16)
            )
            for addr in get_addresses()
        ],
        'tests': [
            {
                'function': ContractFunction(
                    'transfer', ('address', 'uint256')),
                'iterations': 100
            },
            {
                'function': ContractFunction(
                    'approve', ('address', 'uint256')),
                'iterations': 100
            },
        ]
    }

]
