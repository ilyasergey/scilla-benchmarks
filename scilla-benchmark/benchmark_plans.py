from utils import SENDER_ADDRESS, addresses


def get_benchmark_plans(state_entries, test_iterations):
    benchmark_plans = [
        {
            'contract': 'fungible-token',
            'tests': [
                {
                    'test_name': 'Transfer',
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
                }
            ]
        }
    ]
    return benchmark_plans
