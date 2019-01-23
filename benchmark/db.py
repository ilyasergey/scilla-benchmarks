import os
import plyvel

current_dir = os.path.dirname(os.path.realpath(__file__))
db_dir = os.path.join(current_dir, 'evm-data', 'evm')


def calculate_all_db_key_value_sizes():
    db = plyvel.DB(db_dir)
    snapshot = db.snapshot()
    key_sizes = 0
    value_sizes = 0
    key_count = 0

    with snapshot.iterator() as it:
        for key, value in it:
            key_count += 1
            key_sizes += len(key)
            value_sizes += len(value)
    return key_sizes + value_sizes


def main():
    print('Key sizes:', sum(key_sizes))
    print('Value sizes:', sum(value_sizes))
    print('Key & value sizes:', sum(key_sizes)+sum(value_sizes))


if __name__ == '__main__':
    main()
