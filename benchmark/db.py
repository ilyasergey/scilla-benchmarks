import os
import plyvel

current_dir = os.path.dirname(os.path.realpath(__file__))
db_dir = os.path.join(current_dir, 'evm-data', 'evm')


def main():
    db = plyvel.DB(db_dir)
    print(db)


if __name__ == '__main__':
    main()
