import sqlite3
import argparse
from importlib.resources import files

from ..util.db_path_config import write_db_path


def migrate_db(db_path: str) -> None:
    schema_path = files("nova_memory._db.db").joinpath("schema.sql")

    try:
        with open(schema_path, 'r') as FILE:
            text = FILE.read()
        statements = [statement.strip() for statement in text.split(';')]
    except FileNotFoundError:
        print(f'Could not find DB')
        exit()

    with sqlite3.Connection(db_path) as conn:
        cursor = conn.cursor()
        for statement in statements:
            try:
                cursor.execute(statement)
                conn.commit()
            except Exception as err:
                print(f'\n{str(err)}\n\nStatement: {statement}')
                continue
    write_db_path(db_path)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db-path", required=True)
    args = p.parse_args()
    
    migrate_db(args.db_path)
            
if __name__ == '__main__':
    main()

    


    
