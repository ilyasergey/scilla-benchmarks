import os
import plyvel

current_dir = os.path.dirname(os.path.realpath(__file__))
db_dir = os.path.join(current_dir, 'evm-data', 'evm')
db = plyvel.DB(db_dir)


# def measure_item_size(db, key):
#     db.get(key)


def main():

    for key, value in db:
        print(key, value)


if __name__ == '__main__':
    main()
