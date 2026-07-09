# 🏥 Hospital — Patient Management System

A desktop application for managing hospital patients (clients), their appointments and billing.
The **data layer is written in C** (compiled to a shared library) and exposed to a **Python / Tkinter graphical interface** through `ctypes`. Patient records are persisted in CSV files.

> Academic project — UTT, course **NF06**.

---

## ✨ Features

- **List patients** — display all patients by last / first name.
- **Add a patient** — full form with field validation (numeric vs. text).
- **Update / delete a patient** — deleted patients are archived in a history file instead of being lost.
- **Search** — by ID or by last name.
- **Sort & filter** — alphabetically (A–Z) or by service type (Emergency / Consultation).
- **Billing** — automatically compute a patient's bill from the requested medical service + number of nights.
- **Statistics** — count patients per service type and per medical specialty.

---

## 🏗️ Architecture

```
┌─────────────────────────────┐
│   Python / Tkinter (GUI)    │   App.py, Window.py, main.py
│   ─ views, forms, stats     │
└──────────────┬──────────────┘
               │  ctypes  (ClientAPI.py)
┌──────────────▼──────────────┐
│      C shared library       │   CSVFile.c  →  lib_csvFile.dll
│  ─ CRUD, search, sort, bill │
└──────────────┬──────────────┘
               │
┌──────────────▼──────────────┐
│         CSV storage         │   db/clients.csv
│                             │   db/deleted_clients.csv (history)
└─────────────────────────────┘
```

### Components

| File | Role |
|------|------|
| `c/CSVFile.c` | Core logic in C: read/write/update/delete CSV rows, search, sort (`qsort`), filter, and bill computation. Compiled to `lib_csvFile.dll`. |
| `python/ClientAPI.py` | `ctypes` bridge. Defines the `Client` struct, loads the DLL and wraps every C function into a clean Python API. |
| `python/App.py` | Main window: patient list, search bars, sort dropdown, "Add" and "Stats" buttons. |
| `python/Window.py` | Secondary windows: add user, view/edit user, billing (`ServiceWindow`) and statistics (`StatsWindow`). |
| `python/main.py` | Entry point — wires `ClientAPI` into `App` and starts the GUI. |

### Patient data model

Each record (C `Client` struct / CSV row) holds:

```
id, service_type, first_name, last_name, address, age, sex, illness,
room_number, specialty, doctor, date, time, nights, service
```

### Billing rates (defined in `countBill`, in euros)

| Service | Price | Service | Price |
|---|---|---|---|
| Childbirth | 2600 | Ultrasound | 85 |
| Health check-up | 50 | Colonoscopy | 190 |
| Carpal tunnel operation | 1250 | MRI | 400 |
| ENT | 35 | Room (per night) | 68 |

Total bill = service price + `nights × 68`.

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+** with Tkinter (bundled with the standard Windows Python installer).
- A **C compiler** and **CMake** (e.g. MinGW-w64 / GCC) to build the shared library.
- The project targets **Windows** (the Python code loads `lib_csvFile.dll`).

### 1. Build the C shared library

The Python side expects `c/lib_csvFile.dll`. A prebuilt DLL is included, but to rebuild it from source compile `CSVFile.c` as a shared library:

```bash
cd c
gcc -shared -o lib_csvFile.dll CSVFile.c
```

> The provided `CMakeLists.txt` builds a standalone executable; for use with the GUI you need the **shared library** (`.dll`) as shown above.

### 2. Run the application

```bash
cd python
python main.py
```

The GUI reads from and writes to `python/db/clients.csv` (and archives deletions to `python/db/deleted_clients.csv`).

---

## 📁 Project structure

```
Hospital/
├── c/
│   ├── CSVFile.c              # C data-layer source
│   ├── CMakeLists.txt         # build configuration
│   ├── lib_csvFile.dll        # prebuilt shared library
│   ├── db/clients.csv         # sample data
│   ├── html/  latex/          # Doxygen-generated documentation
│   └── cmake-build-debug/     # build artifacts
├── python/
│   ├── main.py                # entry point
│   ├── App.py                 # main window
│   ├── Window.py              # secondary windows
│   ├── ClientAPI.py           # ctypes bridge to the DLL
│   └── db/
│       ├── clients.csv        # active patients
│       └── deleted_clients.csv# deletion history
└── Documentation pour les utilisateurs de l'application "Hôpital".pdf
```

---

## 📖 Documentation

- **User guide** (French): `Documentation pour les utilisateurs de l'application "Hôpital".pdf`
- **API reference**: Doxygen-generated docs for the C library in `c/html/index.html`.

---

## ⚠️ Notes & limitations

- The application is **Windows-oriented** (loads a `.dll` and uses relative paths such as `../c/lib_csvFile.dll` — run it from the `python/` directory).
- Storage is plain CSV with a fixed line length (`MAX_LINE_LENGTH = 256`); commas inside fields are not supported.
- IDs are generated from the first 4 digits of a UUID and are not guaranteed collision-free at scale.

---

## 📝 License

Academic project — provided as-is for educational purposes.
