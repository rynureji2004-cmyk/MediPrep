"""
MediPrep - Procedure Rooms Seeding Script
Populates standard preparation areas and scanning/procedure rooms in tbl_procedure_rooms.
Does not delete or duplicate existing records.
"""

import sys
import os

# Add root folder to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from database import DatabaseManager, DBTransactionContext, DBConnectionContext
from config import config_by_name

# Standard Preparation Rooms
GLOBAL_PREP_ROOMS = [
    "Pre-Procedure Preparation Room 1",
    "Pre-Procedure Preparation Room 2",
    "General Patient Preparation Room"
]

# Standard Procedure / Scanning Rooms by Category / Keyword
def get_rooms_for_procedure(proc_id, proc_name, proc_category, proc_code):
    prep_rooms = list(GLOBAL_PREP_ROOMS)
    proc_rooms = []

    name_lower = (proc_name or "").lower()
    cat_lower = (proc_category or "").lower()
    code_lower = (proc_code or "").lower()

    if "mri" in name_lower or "mri" in code_lower:
        prep_rooms.append("MRI Preparation Room")
        proc_rooms.extend(["MRI Scanning Room 1", "MRI Scanning Room 2"])
    elif "ct" in name_lower or "ct" in code_lower:
        prep_rooms.append("CT Prep Bay")
        proc_rooms.extend(["CT Scanning Room 1", "CT Scanner Room 2"])
    elif "endoscop" in name_lower or "colonoscop" in name_lower or "gastro" in cat_lower:
        prep_rooms.append("Endoscopy Preparation Room")
        proc_rooms.extend(["Endoscopy Room 1", "Endoscopy Suite A", "Endoscopy Suite B"])
    elif "cardiac" in name_lower or "heart" in name_lower or "ecg" in name_lower or "cardio" in cat_lower:
        prep_rooms.append("Cardiac Pre-Procedure Room")
        proc_rooms.extend(["Cardiac Procedure Room 1", "Cath Lab 1", "Cath Lab 2"])
    elif "ortho" in name_lower or "arthroscop" in name_lower or "ortho" in cat_lower:
        prep_rooms.append("Orthopedic Preparation Room")
        proc_rooms.extend(["Orthopedic Procedure Room 1", "General Procedure Room 1"])
    else:
        prep_rooms.append("Surgical Prep Unit")
        proc_rooms.extend(["General Procedure Room 1", "General Surgery OR 5", "General Surgery OR 6"])

    # Ensure unique while preserving order
    unique_prep = []
    for r in prep_rooms:
        if r not in unique_prep:
            unique_prep.append(r)

    unique_proc = []
    for r in proc_rooms:
        if r not in unique_proc:
            unique_proc.append(r)

    return unique_prep, unique_proc


def seed_rooms(env='development'):
    print(f"Initializing connection pool for {env} environment...")
    config = config_by_name[env]
    DatabaseManager.initialize_pool(
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        pool_size=5,
        pool_name='room_seed_pool'
    )

    with DBConnectionContext() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, code, name, category FROM tbl_procedures")
            procedures = cursor.fetchall()

    if not procedures:
        print("No procedures found in tbl_procedures.")
        return 0

    total_inserted = 0
    with DBTransactionContext() as cursor:
        for proc in procedures:
            pid = proc['id']
            pname = proc['name']
            prep_rooms, proc_rooms = get_rooms_for_procedure(pid, pname, proc.get('category'), proc.get('code'))

            # Insert preparation rooms
            for room in prep_rooms:
                cursor.execute("""
                    SELECT id FROM tbl_procedure_rooms 
                    WHERE procedure_id = %s AND room_type = 'preparation' AND room_name = %s
                """, (pid, room))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO tbl_procedure_rooms (procedure_id, room_type, room_name)
                        VALUES (%s, 'preparation', %s)
                    """, (pid, room))
                    total_inserted += 1

            # Insert procedure/scanning rooms
            for room in proc_rooms:
                cursor.execute("""
                    SELECT id FROM tbl_procedure_rooms 
                    WHERE procedure_id = %s AND room_type = 'procedure' AND room_name = %s
                """, (pid, room))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO tbl_procedure_rooms (procedure_id, room_type, room_name)
                        VALUES (%s, 'procedure', %s)
                    """, (pid, room))
                    total_inserted += 1

    print(f"Seeding completed successfully. Inserted {total_inserted} new room records without modifying existing data.")
    return total_inserted


if __name__ == '__main__':
    seed_rooms()
