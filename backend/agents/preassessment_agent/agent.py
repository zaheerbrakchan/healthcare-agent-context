import os
import json
import re
from tools.appointment.patient_api import get_patient_details
from tools.preassesment.preassessment_api import save_preassessment
from agents.shared_context import get_shared_context
from services.llm_service import query_llm

class PreassessmentAgent:
    MAX_HISTORY = 5

    def __init__(self):
        prompt_path = os.path.join(
            os.path.dirname(__file__),
            "prompts",
            "preassessment_agent.txt"
        )
        with open(prompt_path, encoding="utf-8") as f:
            self.system_prompt = f.read()

        self.conversation_history = []
        self.session_context = {
            "patient_id": None,
            "patient_name": None,
            "phone_no": None  # store phone number
        }

    def handle_aquery(self, user_query: str, patient_phone: str = None):
        # Step 1 – check if patient already fetched
        if not self.session_context["patient_id"]:
            # Try to use phone from session, argument, or extract from user input
            phone = self.session_context.get("phone_no") or patient_phone or self._extract_phone(user_query)
            if not phone:
                reply = "Hello! Welcome to ABC Hospital. Could you please share your registered phone number to get started?"
                self._update_history(user_query, reply)
                return {"action": "ask_clarification", "parameters": {}, "reply": reply}

            # Save phone in session
            self.session_context["phone_no"] = phone

            # Fetch patient details
            patient = get_patient_details(phone)
            if not patient:
                reply = "I couldn't find your record. Are you sure the phone number is correct?"
                self._update_history(user_query, reply)
                return {"action": "ask_clarification", "parameters": {}, "reply": reply}

            # Update session
            self.session_context.update({
                "patient_id": patient["id"],
                "patient_name": patient["name"]
            })

            # Fetch shared context dynamically
            shared_summary = get_shared_context("appointment_summary")
            if shared_summary:
                prompt = f"You are a friendly preassessment assistant. Generate a human-friendly reply to the patient, using these notes from their appointment:\n{shared_summary}\nThen transition to collecting preassessment details."
                llm_reply = query_llm(self.system_prompt, prompt)
            else:
                llm_reply = f"Thanks, {patient['name']}! Now let's start with your preassessment."

            self._update_history(user_query, llm_reply)
            return {"action": "ask_clarification", "parameters": {}, "reply": llm_reply}

        # Step 2 – Collect preassessment info
        save_preassessment(
            patient_id=self.session_context["patient_id"],
            chief_complaint=user_query,  # For simplicity, use user input
            allergies="Not provided",
            family_history="Not provided"
        )
        reply = "Thank you! Your preassessment details have been saved successfully."
        self._update_history(user_query, reply)
        return {"action": "save_preassessment", "parameters": {}, "reply": reply}

    def handle_query(self, user_query: str, patient_phone: str = None):
        # Step 1 – check if patient already fetched
        if not self.session_context["patient_id"]:
            # Try to use phone from session, argument, or extract from user input
            phone = self.session_context.get("phone_no") or patient_phone or self._extract_phone(user_query)
            if not phone:
                reply = "Hello! Welcome to ABC Hospital. Could you please share your registered phone number to get started?"
                self._update_history(user_query, reply)
                return {"action": "ask_clarification", "parameters": {}, "reply": reply}

            # Save phone in session
            self.session_context["phone_no"] = phone

            # Fetch patient details
            patient = get_patient_details(phone)
            if not patient:
                reply = "I couldn't find your record. Are you sure the phone number is correct?"
                self._update_history(user_query, reply)
                return {"action": "ask_clarification", "parameters": {}, "reply": reply}

            # Update session
            self.session_context.update({
                "patient_id": patient["id"],
                "patient_name": patient["name"]
            })

            # Fetch shared context dynamically
            shared_summary = get_shared_context("appointment_summary")
            if shared_summary:
                # Call LLM to generate human-friendly reply referencing previous context
                prompt = f"""
    You are a friendly preassessment assistant. The patient is {patient['name']}.
    You have the following notes from their appointment: {shared_summary}.
    Generate a warm, natural reply acknowledging any patient preferences or requests mentioned in these notes,
    and then transition to collecting preassessment information (chief complaint, allergies, family history).
    """
                llm_reply = query_llm(self.system_prompt, prompt)
            else:
                llm_reply = f"Thanks, {patient['name']}! Now let's start with your preassessment. Could you please tell me your chief complaint, any allergies, and family medical history?"

            self._update_history(user_query, llm_reply)
            return {"action": "ask_clarification", "parameters": {}, "reply": llm_reply}

        # Step 2 – Collect preassessment info
        save_preassessment(
            patient_id=self.session_context["patient_id"],
            chief_complaint=user_query,  # For simplicity, use user input
            allergies="Not provided",
            family_history="Not provided"
        )
        reply = "Thank you! Your preassessment details have been saved successfully."
        self._update_history(user_query, reply)
        return {"action": "save_preassessment", "parameters": {}, "reply": reply}

    def _extract_phone(self, text: str):
        """Simple regex to extract 10-digit phone numbers"""
        match = re.search(r"\b\d{10}\b", text)
        return match.group(0) if match else None

    def _update_history(self, user_query, assistant_reply):
        self.conversation_history.append({
            "user": user_query,
            "assistant": assistant_reply
        })
        if len(self.conversation_history) > self.MAX_HISTORY:
            self.conversation_history = self.conversation_history[-self.MAX_HISTORY:]
