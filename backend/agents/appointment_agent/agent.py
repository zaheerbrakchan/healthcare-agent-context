import json
import os
from datetime import datetime
from tools.appointment.slots_api import get_available_slots, book_appointment
from tools.appointment.patient_api import get_patient_details, register_patient
from services.llm_service import query_llm, get_model_token_limit
from agents.shared_context import update_shared_context



class AppointmentAgent:
    MAX_HISTORY = 5  # keep last 5 conversation turns

    def __init__(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts",
            "appointment_agent.txt"
        )
        with open(prompt_path, encoding="utf-8") as f:
            self.system_prompt = f.read()

        # Conversation memory
        self.conversation_history = []

        # Session memory
        self.session_context = {
            "patient_id": None,
            "patient_name": None,
            "phone_no": None,
            "last_slots": None  # store all fetched slots
        }


    def _summarize_slots(self, slots):
        """Summarize large slot data by doctor & department"""
        if not slots:
            return "No slots available."

        summary = {}
        for s in slots:
            key = f"{s['department']} | {s['doctor_name']}"
            summary[key] = summary.get(key, 0) + 1

        lines = ["Available slots summary:"]
        for k, count in summary.items():
            lines.append(f"{k} – {count} slots")

        return "\n".join(lines)

    def _extract_slot_filters(self, user_query: str, last_slots: list):
        """Use LLM to extract doctor, department, or date filters from user query"""
        if not last_slots:
            return {}

        sample_slots = json.dumps(last_slots[:10], default=str)
        prompt = f"""
You are given the following sample slot data:

{sample_slots}

A patient asked: "{user_query}"

Extract any filters the patient is requesting as a JSON with keys:
doctor_name, department, start_date, end_date (dates in YYYY-MM-DD), start_time, end_time (optional).

If a filter is not mentioned, set its value to null.
Only return JSON.
"""
        llm_output = query_llm(self.system_prompt, prompt)
        try:
            filters = json.loads(llm_output)
        except json.JSONDecodeError:
            filters = {}
        return {k: v for k, v in filters.items() if v}  # remove nulls

    def _filter_slots(self, slots, filters: dict):
        """Filter last_slots based on doctor, department, or date"""
        result = []
        for s in slots:
            if filters.get("doctor_name") and filters["doctor_name"].lower() not in s.get("doctor_name", "").lower():
                continue
            if filters.get("department") and filters["department"].lower() not in s.get("department", "").lower():
                continue
            if filters.get("start_date") and s["start_datetime"].date() < datetime.fromisoformat(filters["start_date"]).date():
                continue
            if filters.get("end_date") and s["start_datetime"].date() > datetime.fromisoformat(filters["end_date"]).date():
                continue
            result.append(s)
        return result

    def handle_query(self, user_query: str, patient_phone: str = None):
        """Main handler"""
        slot_summary = ""
        last_slots = self.session_context.get("last_slots")

        # Handle intelligent slot filtering only if last_slots exist
        if last_slots:
            filters = self._extract_slot_filters(user_query, last_slots)
            filtered_slots = self._filter_slots(last_slots, filters) if filters else last_slots

            # Decide whether to send full data or summary
            slots_text = json.dumps(filtered_slots, default=str)
            approx_tokens = len(slots_text) / 4
            if approx_tokens <= get_model_token_limit("gpt-4"):
                slot_summary = slots_text
            else:
                slot_summary = self._summarize_slots(filtered_slots)

        llm_prompt = self._build_llm_prompt(user_query, slot_summary)
        print("LLM Prompt:\n", llm_prompt)

        llm_output = query_llm(self.system_prompt, llm_prompt)

        try:
            response_json = json.loads(llm_output)
        except json.JSONDecodeError:
            reply = "Sorry, I didn’t quite get that. Could you please repeat?"
            self._update_history(user_query, reply)
            return reply

        action = response_json.get("action", "").strip().lower()
        params = response_json.get("parameters", {})
        reply = response_json.get("reply", "")
        print("action : ",action)
        print("reply : ", reply)
        print("params : ", params)

        # 1️⃣ Get patient details
        if action == "get_patient_details":
            phone = params.get("phone_no")
            if not phone:
                reply = "Please share your registered phone number."
            else:
                patient = get_patient_details(phone)
                if patient:
                    reply = f"Welcome back, {patient['name']}! How can I assist you today?"
                    self.session_context.update({
                        "patient_id": patient["id"],
                        "patient_name": patient["name"],
                        "phone_no": phone
                    })
                else:
                    reply = "I couldn’t find your record. Would you like to register?"

        # 2️⃣ Register new patient
        elif action == "register_patient":
            required_fields = ["name", "age", "gender", "phone_no"]
            if not all(params.get(f) for f in required_fields):
                reply = "Please provide name, age, gender, and phone number."
            else:
                patient = register_patient(params)
                self.session_context.update({
                    "patient_id": patient["id"],
                    "patient_name": patient["name"],
                    "phone_no": patient["phone_no"]
                })
                reply = f"✅ Registration successful! Welcome, {patient['name']}."

        # 3️⃣ Get available slots
        elif action == "get_available_slots":
            slots = get_available_slots(
                doctor_name=params.get("doctor_name"),
                department=params.get("department"),
                start_datetime=params.get("start_datetime"),
                end_datetime=params.get("end_datetime")
            )
            self.session_context["last_slots"] = slots

            # Decide whether to send full data or summary
            slots_text = json.dumps(slots, default=str)
            approx_tokens = len(slots_text) / 4
            if approx_tokens <= get_model_token_limit("gpt-4"):
                # 🧍 Human-readable display (instead of JSON)
                lines = ["Here are the available slots:\n"]
                for s in slots:
                    start = s["start_datetime"].strftime("%d %b %Y, %I:%M %p")
                    end = s["end_datetime"].strftime("%I:%M %p")
                    lines.append(f"🩺 Slot ID: {s['slot_id']} – Dr. {s['doctor_name']} ({s['department']}) – {start} to {end}")
                reply = "\n".join(lines)
            else:
                reply = self._summarize_slots(slots)

        elif action == "book_appointment":
            slot_id = params.get("slot_id")
            patient_id = params.get("patient_id")
            if not slot_id or not patient_id:
                reply = "Please confirm patient ID and slot ID."
            else:
                confirmation = book_appointment(slot_id, patient_id)
                print("confirmation : ",confirmation)
                if confirmation.get("status") == "Booked":
                    reply = "✅ Appointment successfully booked!"

                    # free huge memory
                    self.session_context["last_slots"] = None
                else:
                    reply = "Sorry, booking failed. Try another slot."


        # 5️⃣ Ask clarification
        elif action == "ask_clarification":
            reply = reply or "Could you please clarify that?"

        # 6️⃣ Default fallback
        else:
            reply = reply or "How can I assist you with appointments today?"


        # Save conversation turn
        self._update_history(user_query, reply)
        # 🧠 Generate conversation summary for cross-agent context sharing
        try:
            summary = self._generate_summary()
            update_shared_context("appointment_summary", summary)
            print("\n--- Shared context updated with appointment summary ---")
            print(summary)
            print("--------------------------------------------------------\n")
        except Exception as e:
            print("Error generating shared summary:", e)

        # Return raw text
        return reply


    def _build_llm_prompt(self, user_query: str, slot_summary: str = ""):
        """Build LLM prompt including context, conversation (without slot data), and optional slot summary"""
        patient_name = self.session_context.get("patient_name")
        patient_id = self.session_context.get("patient_id")

        context_info = ""
        if patient_name or patient_id:
            context_info = (
                f"(Context: Current patient: {patient_name or 'Unknown'}"
                f"{' (ID: ' + str(patient_id) + ')' if patient_id else ''}.)\n\n"
            )

        # Build clean, token-efficient history (no slot data)
        history_text = ""
        recent_history = self.conversation_history[-self.MAX_HISTORY:]
        for turn in recent_history:
            user_msg = (turn['user'][:500] + "...") if len(turn['user']) > 500 else turn['user']
            assistant_msg = (turn['assistant'][:800] + "...") if len(turn['assistant']) > 800 else turn['assistant']
            history_text += f"Patient: {user_msg}\nAssistant: {assistant_msg}\n"

        # Slot summary is appended temporarily for current LLM call
        prompt = f"""
{context_info}
Below is the ongoing conversation between Nicole (assistant) and a patient.
Continue naturally, based on the context and slot summary.

{history_text}


Patient: {user_query}
Assistant:
"""
        return prompt


    def _update_history(self, user_query: str, assistant_reply: str):
        """Save only short user/assistant turns — skip slot JSON or summaries"""
        # Filter out long slot dumps
        if "Available slots summary" in assistant_reply or assistant_reply.strip().startswith("[{"):
            clean_reply = "[Slots information shown to user]"  # placeholder for context
        else:
            clean_reply = assistant_reply

        self.conversation_history.append({
            "user": user_query,
            "assistant": clean_reply
        })

        # Trim history length
        if len(self.conversation_history) > self.MAX_HISTORY:
            self.conversation_history = self.conversation_history[-self.MAX_HISTORY:]

    def _generate_summary(self):
        """Summarize the last few turns for cross-agent context sharing."""
        if not self.conversation_history:
            return "No prior conversation available to summarize."

        convo = " ".join([
            f"User: {t['user']} Assistant: {t['assistant']}"
            for t in self.conversation_history[-5:]
        ])

        summary_prompt = f"""
 Summarize the key patient details, conditions, and preferences useful for another healthcare agent (like preassessment).
 Focus on things the patient mentioned that won't be in hospital database records
 (e.g., accessibility needs, personal notes, fatigue, or comfort preferences).

 Conversation:
 {convo}
 """
        summary = query_llm("You are a helpful summarizer for healthcare context.", summary_prompt)
        return summary.strip()

