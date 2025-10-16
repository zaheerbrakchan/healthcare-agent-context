from db import DATABASE_URL
from sqlalchemy import text, create_engine, select, table, column, bindparam

engine = create_engine(DATABASE_URL)


def get_availauuble_slots(start_datetime, end_datetime, doctor_name=None, department=None):
    print("inside get_available_slots !!!")
    params = {"start_datetime": start_datetime, "end_datetime": end_datetime}
    base_query = """
        SELECT *
        FROM resource_calendar
        WHERE status = 'Available'
        AND start_datetime >= :start_datetime
        AND end_datetime <= :end_datetime
    """

    with engine.connect() as conn:
        resource_ids = []

        # 🔍 1. Find doctor IDs (if doctor_name given)
        if doctor_name:
            doctor_query = text("""
                SELECT id
                FROM doctors
                WHERE name ILIKE :doctor_name
            """)
            rows = conn.execute(doctor_query, {"doctor_name": f"%{doctor_name}%"}).fetchall()
            resource_ids = [row.id for row in rows]
            print("resource_ids", resource_ids)
            if not resource_ids:
                return []

        # 🔍 2. Add filters dynamically
        if resource_ids:
            base_query += " AND resource_id IN :resource_ids"
            params["resource_ids"] = tuple(resource_ids)

        if department:
            base_query += " AND department ILIKE :department"
            params["department"] = f"%{department}%"

        base_query += " ORDER BY start_datetime ASC"

        # ✅ 3. Fix parameter expansion for resource_ids
        query = text(base_query)
        if "resource_ids" in params:
            query = query.bindparams(bindparam("resource_ids", expanding=True))

        print("query:", query)
        print("params:", params)

        rows = conn.execute(query, params).fetchall()
        return [dict(row._mapping) for row in rows]

def get_available_slots(start_datetime, end_datetime, doctor_name=None, department=None):
        print("inside get_available_slots !!!")
        params = {"start_datetime": start_datetime, "end_datetime": end_datetime}

        base_query = """
            SELECT rc.*, d.name AS doctor_name
            FROM resource_calendar rc
            JOIN doctors d ON rc.resource_id = d.id
            WHERE rc.status = 'Available'
            AND rc.start_datetime >= :start_datetime
            AND rc.end_datetime <= :end_datetime
        """

        with engine.connect() as conn:
            resource_ids = []

            # 🔍 1. Filter by doctor_name if provided
            if doctor_name:
                doctor_query = text("""
                    SELECT id
                    FROM doctors
                    WHERE name ILIKE :doctor_name
                """)
                rows = conn.execute(doctor_query, {"doctor_name": f"%{doctor_name}%"}).fetchall()
                resource_ids = [row.id for row in rows]
                print("resource_ids", resource_ids)
                if not resource_ids:
                    return []

            # 🔍 2. Apply additional filters
            if resource_ids:
                base_query += " AND rc.resource_id IN :resource_ids"
                params["resource_ids"] = tuple(resource_ids)

            if department:
                base_query += " AND rc.department ILIKE :department"
                params["department"] = f"%{department}%"

            base_query += " ORDER BY rc.start_datetime ASC"

            # ✅ 3. Handle expanding param for resource_ids
            query = text(base_query)
            if "resource_ids" in params:
                query = query.bindparams(bindparam("resource_ids", expanding=True))

            print("query:", query)
            print("params:", params)

            rows = conn.execute(query, params).fetchall()
            return [dict(row._mapping) for row in rows]


def book_appointment(slot_id, patient_id):
    print("patient_id:", patient_id)
    print("slot_id:", slot_id)
    with engine.connect() as conn:
        conn.execute(
            text("UPDATE resource_calendar SET status='Booked', patient_id=:pid WHERE slot_id=:sid"),
            {"pid": patient_id, "sid": slot_id}
        )
        conn.commit()
        return {"slot_id": slot_id, "status": "Booked"}
