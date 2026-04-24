import sqlite3

def sync_dbs():
    conn1 = sqlite3.connect('../backend_browse/db.sqlite3')
    conn2 = sqlite3.connect('db.sqlite3')
    c1 = conn1.cursor()
    c2 = conn2.cursor()

    c2.execute('DELETE FROM my_request_material')
    c2.execute('DELETE FROM my_request_category')

    # Categories
    # Let's see what inventory_category has
    cat_columns = [desc[0] for desc in c1.execute('SELECT * FROM inventory_category').description]
    # likely 'id', 'name'
    if 'name' in cat_columns:
        cats = c1.execute('SELECT id, name FROM inventory_category').fetchall()
    elif 'title' in cat_columns:
        cats = c1.execute('SELECT id, title FROM inventory_category').fetchall()
    
    for row in cats:
        c2.execute('INSERT INTO my_request_category (id, name) VALUES (?, ?)', row)

    # Materials
    mats = c1.execute(
        "SELECT id, title, category_id, description, quantity, 'unit', 'REF-' || id FROM inventory_material"
    ).fetchall()
    
    for row in mats:
        c2.execute(
            'INSERT INTO my_request_material (id, name, category_id, description, quantity_available, unit, reference) VALUES (?, ?, ?, ?, ?, ?, ?)',
            row
        )

    conn2.commit()
    print("ALL MATERIALS SYNCED SUCCESSFULLY BETWEEN DATABASES!")

if __name__ == '__main__':
    sync_dbs()
