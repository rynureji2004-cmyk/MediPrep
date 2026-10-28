class RulesEngine:
    """CLINICAL SAFETY RULES ENGINE: Predefined deterministic rule evaluation (No AI / Machine Learning)."""

    @staticmethod
    def evaluate_vitals(vitals):
        """
        Runs clinical safety rules on patient lab metrics.
        Returns a list of warning messages.
        """
        suggestions = []
        
        if not vitals:
            return suggestions

        # Rule 1: Blood Sugar threshold
        blood_sugar = vitals.get('blood_sugar')
        if blood_sugar is not None:
            try:
                if float(blood_sugar) > 200:
                    suggestions.append("⚠️ CLINICAL REVIEW REQUIRED: Blood sugar result (>200 mg/dL) requires doctor review.")
            except (ValueError, TypeError):
                pass

        # Rule 2: Hemoglobin threshold
        hemoglobin = vitals.get('hemoglobin')
        if hemoglobin is not None:
            try:
                if float(hemoglobin) < 10:
                    suggestions.append("⚠️ CLINICAL REVIEW REQUIRED: Low Hemoglobin (<10 g/dL) detected.")
            except (ValueError, TypeError):
                pass

        # Rule 3: Blood Pressure (Systolic / Diastolic)
        systolic = vitals.get('systolic_bp')
        diastolic = vitals.get('diastolic_bp')
        if systolic is not None or diastolic is not None:
            try:
                systolic_val = int(systolic) if systolic else 0
                diastolic_val = int(diastolic) if diastolic else 0
                if systolic_val > 140 or diastolic_val > 90:
                    suggestions.append("⚠️ CLINICAL REVIEW REQUIRED: Elevated Blood Pressure (>140/90 mmHg) detected.")
            except (ValueError, TypeError):
                pass

        # Rule 4: Temperature threshold
        temp = vitals.get('temperature')
        if temp is not None:
            try:
                if float(temp) > 100.4:
                    suggestions.append("⚠️ CLINICAL REVIEW REQUIRED: Fever (>100.4°F) detected. Potential sign of infection.")
                elif float(temp) < 95.0:
                    suggestions.append("⚠️ CLINICAL REVIEW REQUIRED: Low body temperature (<95°F) detected.")
            except (ValueError, TypeError):
                pass

        # Rule 5: Creatinine threshold
        creatinine = vitals.get('creatinine')
        if creatinine is not None:
            try:
                if float(creatinine) > 1.5:
                    suggestions.append("⚠️ CLINICAL REVIEW REQUIRED: Elevated Creatinine (>1.5 mg/dL). Kidney function warning.")
            except (ValueError, TypeError):
                pass

        return suggestions
