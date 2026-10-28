from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class RemindersService:
    """Clinical Reminder Engine (No AI). Generates pre-op checklist action reminders for patients."""

    @staticmethod
    def get_active_reminders(checklist, scheduled_at_str):
        """
        Evaluates active patient checklist items and scheduled procedure date.
        Returns a list of structured reminder strings.
        """
        reminders = []
        if not scheduled_at_str:
            return reminders

        # Parse procedure datetime
        try:
            if isinstance(scheduled_at_str, str):
                scheduled_at = datetime.strptime(scheduled_at_str, "%Y-%m-%d %H:%M:%S")
            else:
                scheduled_at = scheduled_at_str
        except Exception:
            try:
                scheduled_at = datetime.strptime(scheduled_at_str.replace('T', ' '), "%Y-%m-%d %H:%M:%S")
            except Exception:
                return reminders

        now = datetime.now()
        tomorrow = now + timedelta(days=1)

        # 1. Reminder: Procedure Tomorrow
        if now.date() < scheduled_at.date() <= tomorrow.date():
            reminders.append("Procedure Tomorrow: Your surgery is scheduled for tomorrow. Please review all guidelines.")

        # Evaluate checklist items
        for item in checklist:
            status = item.get('status')

            # Only remind for incomplete/pending tasks
            if status == 'pending':
                task_name = item.get('task_name', '').strip()
                description = item.get('description', '').strip()

                if task_name:
                    # Clean up description formatting
                    if description:
                        if not description.endswith('.') and not description.endswith('!') and not description.endswith('?'):
                            description += '.'
                        reminder = f"{task_name}: {description}"
                    else:
                        reminder = f"{task_name}."

                    if reminder not in reminders:
                        reminders.append(reminder)

        return reminders
