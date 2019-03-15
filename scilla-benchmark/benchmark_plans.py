from utils import SENDER_ADDRESS, addresses


def get_benchmark_plans(state_entries, test_iterations):
    benchmark_plans = [
        {
            'contract': 'fungible-token',
            'state':  [
                {
                    "vname": "_balance",
                    "type": "Uint128",
                    "value": "0"
                },
                {
                    "vname": "balances",
                    "type": "Map (ByStr20) (Uint128)",
                    "value": [
                        {
                            "key": SENDER_ADDRESS,
                            "val": "1000000"
                        }
                    ]+[
                        {
                            "key": addr,
                            "val": "1000"
                        }
                        for addr in addresses[:state_entries]
                    ]
                }
            ],
            'tests': [
                {
                    'test_name': 'Transfer',
                    'transactions': [
                        {
                            'transition': 'Transfer',
                            'amount': '0',
                            'sender': SENDER_ADDRESS,
                            'params': [
                                {
                                    'vname': 'to',
                                    'type': 'ByStr20',
                                    'value': '0x44345678901234567890123456789012345678cd'
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
                            'amount': '0',
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


        {
            'contract': 'nonfungible-token',
            'state':  [
                {
                    "vname": "_balance",
                    "type": "Uint128",
                    "value": "0"
                },
                {
                    "vname": "tokenOwnerMap",
                    "type": "Map (Uint256) (ByStr20)",
                    "value": [
                        {
                            "key": str(index),
                            "val": SENDER_ADDRESS
                        }
                        for index in range(state_entries)
                    ]
                }
            ],
            'tests': [
                {
                    'test_name': 'approve',
                    'transactions': [
                        {
                            'transition': 'approve',
                            'amount': '0',
                            'sender': SENDER_ADDRESS,

                            'params': [
                                {
                                    'vname': 'to',
                                    'type': 'ByStr20',
                                    'value': addr,
                                },
                                {
                                    'vname': 'tokenId',
                                    'type': 'Uint256',
                                    'value': str(index),
                                },
                            ]
                        }
                        for index, addr in enumerate(addresses[:test_iterations])
                    ]
                },
                {
                    'test_name': 'setApprovalForAll',
                    'transactions': [
                        {
                            'transition': 'setApprovalForAll',
                            'amount': '0',
                            'sender': SENDER_ADDRESS,
                            'params': [
                                {
                                    'vname': 'to',
                                    'type': 'ByStr20',
                                    'value': addr,
                                },
                                {
                                    "vname": "approved",
                                    "type": "Bool",
                                    "value": {
                                        "constructor": "True",
                                        "argtypes": [],
                                        "arguments": []
                                    }
                                }
                            ]
                        }
                        for index, addr in enumerate(addresses[:test_iterations])
                    ]
                }
            ]
        },


        {
            'contract': 'auction',
            'state':  [
                {
                    "vname": "_balance",
                    "type": "Uint128",
                    "value": "1000000"
                },
                {"vname": "highestBid", "type": "Uint128", "value": "100"},
                {
                    "vname": "highestBidder",
                    "type": "Option (ByStr20)",
                    "value": {
                        "constructor": "Some",
                        "argtypes": ["ByStr20"],
                        "arguments": [SENDER_ADDRESS]
                    }
                },
                {
                    "vname": "pendingReturns",
                    "type": "Map (ByStr20) (Uint128)",
                    "value": [
                        {
                            "key": addr,
                            "val": '10'
                        }
                        for addr in addresses[:state_entries]
                    ]
                },
                {
                    "vname": "ended",
                    "type": "Bool",
                    "value": {"constructor": "False", "argtypes": [], "arguments": []}
                }
            ],
            'tests': [
                {
                    'test_name': 'Bid',
                    'transactions': [
                        {
                            'transition': 'Bid',
                            'amount': '1000',
                            'sender': addr,
                            'params': []
                        }
                        for addr in addresses[:test_iterations]
                    ]
                },
                {
                    'test_name': 'Withdraw',
                    'transactions': [
                        {
                            'transition': 'Withdraw',
                            'amount': '0',
                            'sender': addr,
                            'params': []
                        }
                        for addr in addresses[:test_iterations]
                    ]
                },

            ]
        },


        {
            'contract': 'crowdfunding',
            'state':  [
                {
                    "vname": "_balance",
                    "type": "Uint128",
                    "value": "1000000"
                },
                {
                    "vname": "backers",
                    "type": "Map (ByStr20) (Uint128)",
                    "value": [
                        {
                            "key": addr,
                            "val": '1000'
                        }
                        for addr in addresses[:state_entries]
                    ]
                },
                {
                    "vname": "funded",
                    "type": "Bool",
                    "value": {"constructor": "False", "argtypes": [], "arguments": []}
                }
            ],
            'tests': [
                {
                    'test_name': 'Donate',
                    'transactions': [
                        {
                            'transition': 'Donate',
                            'amount': '100',
                            'sender': addr,
                            'params': []
                        }
                        for addr in addresses[:test_iterations]
                    ]
                },
                {
                    'test_name': 'GetFunds',
                    'blockchain': 'blockchain-getfunds.json',
                    'transactions': [
                        {
                            'transition': 'GetFunds',
                            'amount': '0',
                            'sender': SENDER_ADDRESS,
                            'params': []
                        }
                        for addr in addresses[:test_iterations]
                    ]
                },
            ]
        }
    ]
    return benchmark_plans
