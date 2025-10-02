from fastmcp import FastMCP
import sqlite3
import os 

DB_path = os.path.join(os.path.dirname(__file__),"expense.db")

mcp = FastMCP(name="Testing")

def init_db():
    with sqlite3.connect(DB_path) as c:
        c.execute("""
            CREATE TABLE IF NOT EXISTS EXPENSES(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                subcategory TEXT DEFAULT '',
                note TEXT DEFAULT ''
                )
            """)

init_db()

@mcp.tool()
def add_expense(date, amount, category, subcategory = '', note = ''):
    """Add a new expenceentry in the Database."""
    with sqlite3.connect(DB_path) as c:
        cur = c.execute(
            "INSERT INTO Expenses(date, amount, category, subcategory, note) VALUES (?,?,?,?,?)",
            (date,amount,category,subcategory,note)
        )
        c.commit()
        return {"status":"ok","id":cur.lastrowid}

@mcp.tool()
def list_expense(start_date,end_date):
    """list All the Expenses that are in the Database."""
    with sqlite3.connect(DB_path) as c:
        cur = c.execute(
            "SELECT * from EXPENSES ORDER BY id ASC"
        )
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols,r)) for r in cur.fetchall()]
    
@mcp.tool()
def update_expense(condition, category=None, date=None, amount=None, subcategory=None, note=None):
    """Update the Expense in the Database by creating condition yourself.
       Example condition: "id = 3" or "category = 'Food'" """
    
    with sqlite3.connect(DB_path) as c:
        query = "UPDATE expenses SET "
        updates = []
        params = []

        # Map column names to given values
        columns = {
            "category": category,
            "date": date,
            "amount": amount,
            "subcategory": subcategory,
            "note": note,
        }

        # Build SET part dynamically
        for col, val in columns.items():
            if val is not None:   # Only update provided fields
                updates.append(f"{col} = ?")
                params.append(val)

        if not updates:
            return {"status": "error", "message": "No fields to update!"}

        query += ", ".join(updates)
        query += f" WHERE {condition}"  # condition must be a valid SQL string

        cur = c.execute(query, params)
        c.commit()

        return {"status": "ok", "rows_updated": cur.rowcount}

if __name__ == "__main__":
    mcp.run(transport="http", host = "0.0.0.0", port = 8000)