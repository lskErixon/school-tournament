# School Tournament Management System

Desktop GUI application for managing a school sports tournament.  
The application is written in **Python (Tkinter)** and uses a **MySQL relational database** with a custom **Repository (DAO) pattern**.

This project was created as a **portfolio / school assignment** and fulfills all required criteria, including database design, transactions, data import, and user-friendly UI.

---

## 1. Installation & Setup
1.1 Clone the repository (open pycharm atd..).

1.2 git clone <REPOSITORY_URL>


<img width="412" height="345" alt="image" src="https://github.com/user-attachments/assets/b4b3462c-58ea-4b21-9045-112804b84e45" />


In pycharm open terminal and past the command:

```bash
cd school-tournament
```

## 2. Create virtual environment (in pycharm open terminal and past the command).
### Windows (PowerShell)

```powershell
### Windows (PowerShell)
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
---

### macOS / Linux

```md
### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Database setup (MySQL Workbench)

  3.1 You can use exists connection or create new(for new conn push "+" like on the screenshot) ->
  
  
  <img width="255" height="301" alt="image" src="https://github.com/user-attachments/assets/6a734c78-0133-44f8-99ac-56d70b3571de" />
  
  <br><br/>
  3.2Create database school_tuornament ->
  3.3 New quary tab -> 
  
  
  <img width="893" height="526" alt="image" src="https://github.com/user-attachments/assets/0b724d06-9e84-4573-8a8a-5626a0699efd" />
  
  <br><br/>
  3.4 Create schema school_tournament ->
  
  
  <img width="601" height="167" alt="image" src="https://github.com/user-attachments/assets/1748bf96-8678-4f0a-9897-72bc593cca37" />
  
  <br><br/>
  3.5 Create tables (copy query from [sql/create_tables.sql](sql/create_tables.sql) and past into MySQL Workbench, execute it) ->
  

  <img width="721" height="841" alt="image" src="https://github.com/user-attachments/assets/c172d191-8411-48ea-979b-8ebb9209039a" />

  <br><br/>
  3.6 Create view (copy query from [sql/create_view.sql](sql/create_view.sql) and past into MySQL Workbench, execute it) -> 


  <img width="930" height="817" alt="image" src="https://github.com/user-attachments/assets/6a2d090e-c046-4430-ab16-876e8fea2b81" />

  
## 4. Application configuration

change config.json fill your data
path: school-tournament/src/config.json
```json
{
  "database": {
    "host": "localhost",
    "port": 3306,
    "user": "school_user",
    "password": "your_password_here",
    "name": "school_tournament"
  }
}
```

## 5. Running the Application

Go to the root directory of the project

Than run the folowing command:
```
python -m src.main
```

The project must be run from the terminal

If the configuration is correct, the application will:

test database connection

open the Tkinter GUI window

## Recommended Usage Order (First Run)
Tournaments – create at least one tournament

Teams – create teams [use teams_test.csv](teams_test.csv)

Players – add players or import CSV [use players_test.csv](players_test.csv)

Referees – create at least one active referee

Matches – create matches (select teams + referees)

Match Events – add goals/cards to matches
   
## Project Goals

- Manage tournaments, teams, players, referees, matches, and match events
- Use a real relational database (MySQL)
- Implement custom Repository (DAO) pattern (**D1 requirement**)
- Provide a desktop GUI usable by non-technical users
- Support CSV data import
- Demonstrate transactions, relations, and error handling

---

## Architecture Overview

- **GUI**: Tkinter (desktop application)
- **Database**: MySQL 8.x
- **Architecture**:
  - Models (dataclasses)
  - Repositories (custom DAO, no ORM)
  - Services (business logic)
  - UI Screens / Dialogs
- **Pattern used**: Repository / DAO pattern (D1)

No ORM (SQLAlchemy, Django ORM, etc.) is used.

---

## Project Structure

```text
school-tournament/
├── .venv/                   # Python virtual environment (not committed)
├── models/                  # Domain models (dataclasses)
│   ├── imports/
│   │   └── __init__.py       # Shared model imports
│   ├── match.py
│   ├── match_event.py
│   ├── match_referee.py
│   ├── player.py
│   ├── referee.py
│   ├── team.py
│   └── tournament.py
├── repositories/            # DAO / Repository layer (D1)
│   ├── match_event_repository.py
│   ├── match_referee_repository.py
│   ├── match_repository.py
│   ├── player_repository.py
│   ├── referee_repository.py
│   ├── team_repository.py
│   └── tournament_repository.py
├── services/                # Business logic
│   └── import_service.py    # CSV import logic
├── src/                     # Core infrastructure
│   ├── config.json          # Local configuration (gitignored)
│   ├── db_mysql.py          # MySQL connection & helpers
│   └── main.py              # Application entry point
├── ui/                      # GUI layer (Tkinter)
│   ├── dialogs/             # Modal dialogs
│   ├── screens/             # Application screens
│   ├── widgets/             # Reusable UI components
│   ├── app.py               # Tkinter bootstrap
│   └── router.py            # Screen navigation
├── players_test.csv         # Sample CSV for player import
├── teams_test.csv           # Sample CSV for team import
├── requirements.txt         # Python dependencies
├── .gitignore
└── README.md
```

---

## Requirements

- **Python 3.12+**
- **MySQL Server 8.x**
- Git (optional)

---

## Python Dependencies

Only one external dependency is used:

mysql-connector-python==9.5.0

Install dependencies using:

```bash
pip install -r requirements.txt
```
---
Rules:

UTF-8 encoding

Comma , delimiter

Column names must match exactly

position ∈ GK, DEF, MID, ATT

## 🔄 Transactions

- Adding a goal event is implemented as a **database transaction**
- Match status automatically changes from **`scheduled` → `live`**
- **Rollback** is performed automatically on error to keep data consistent

## 🧪 Error Handling

- Invalid input validation on **UI level and repository level**
- Database connection errors are handled gracefully
- Foreign key constraint violations are detected and reported
- User-friendly error dialogs are shown to the user

## ✅ Assignment Requirements Fulfilled

- ✔ Real relational database (**MySQL**)
- ✔ 5+ tables with relations
- ✔ M:N relationship (**match ↔ referee**)
- ✔ Custom **DAO / Repository pattern (D1)**
- ✔ Full CRUD operations
- ✔ Transaction across multiple tables
- ✔ CSV import into multiple tables
- ✔ Configuration via config file (`config.json`)
- ✔ GUI usable by non-technical users
- ✔ Error handling and validation

## 📝 Notes

- This is a **desktop application**, not a web application
- No IDE is required to run the application
- The project was developed on a feature branch and later merged into `main`

(It was hard and long to make this project, but with interest, I hope it's not broken and there aren't too many bugs, if you encounter any problems, I apologize, ask the AI ​​what the problem is).
