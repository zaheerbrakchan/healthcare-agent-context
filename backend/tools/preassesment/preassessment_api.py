from db import DATABASE_URL
from sqlalchemy import create_engine, text

engine = create_engine(DATABASE_URL)


def save_preassessment(patient_id, chief_complaint=None, allergies=None, family_history=None, discharge_summaries=None):
    """Save preassessment info for a patient"""
    insert_query = text("""
        INSERT INTO preassessment (patient_id, chief_complaint, allergies, family_history, discharge_summaries, created_at)
        VALUES (:patient_id, :chief_complaint, :allergies, :family_history, :discharge_summaries, NOW())
        RETURNING id
    """)
    with engine.connect() as conn:
        res = conn.execute(
            insert_query,
            {
                "patient_id": patient_id,
                "chief_complaint": chief_complaint,
                "allergies": allergies,
                "family_history": family_history,
                "discharge_summaries": discharge_summaries
            }
        )
        conn.commit()
        row = res.fetchone()
        if row:
            return {"status": "success", "preassessment_id": row[0]}
        else:
            return {"status": "error", "message": "Failed to save preassessment"}



