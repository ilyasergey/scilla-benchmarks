from utils import SENDER_ADDRESS, addresses


def get_benchmark_plans(state_entries, test_iterations):
    benchmark_plans = [
        {
            'contract': 'fungible-token',
            'state':  [{
                "vname": "balances",
                "type": "Map (ByStr20) (Uint128)",
                "value": [
                    {
                        "key": addr,
                        "val": "1000"
                    }
                    for addr in addresses
                ]
            }],
            'tests': [
                {
                    'test_name': 'Transfer',
                    'transactions': [
                        {
                            'transition': 'Transfer',
                            'amount': 0,
                            'sender': SENDER_ADDRESS,
                            'params': [
                                {
                                    'vname': 'to',
                                    'type': 'ByStr20',
                                    'value': addr
                                },
                                {
                                    'vname': 'tokens',
                                    'type': 'Uint128',
                                    'value': '1000'
                                },
                            ],
                        }
                        for addr in addresses[
                            state_entries:state_entries+test_iterations]
                    ]
                },
                {
                    'test_name': 'Approve',
                    'transactions': [
                        {
                            'transition': 'Approve',
                            'amount': 0,
                            'sender': SENDER_ADDRESS,
                            'params': [
                                {
                                    'vname': 'spender',
                                    'type': 'ByStr20',
                                    'value': addr
                                },
                                {
                                    'vname': 'tokens',
                                    'type': 'Uint128',
                                    'value': '1000'
                                },
                            ],
                        }
                        for addr in addresses[
                            state_entries:state_entries+test_iterations]
                    ]
                }
            ]
        },
    ]
    return benchmark_plans
