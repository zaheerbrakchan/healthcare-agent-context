import requests
from db import DATABASE_URL
from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL)

def get_patient_details(phone):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM patient WHERE phone_no = :phone"), {"phone": phone}
        ).fetchone()
        return dict(result._mapping) if result else None

def register_patient(patient_data):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                "INSERT INTO patient(name, age, gender, phone_no) VALUES(:name,:age,:gender,:phone) RETURNING id"
            ),
            patient_data
        )
        patient_id = result.fetchone()[0]
        conn.commit()
        return {"id": patient_id, **patient_data}
