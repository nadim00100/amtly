"""
Form utility functions for validation and analysis
"""

from typing import Dict, List, Optional
from data.form_knowledge_base import FORM_SCHEMAS, REQUIRED_DOCUMENTS


class FormUtils:
    """Utility functions for form processing"""

    @staticmethod
    def get_form_list() -> List[Dict]:
        """Get list of all available forms"""
        forms = []
        for code, data in FORM_SCHEMAS.items():
            forms.append({
                'code': code,
                'name': data['name'],
                'purpose': data['purpose'],
                'pages': data.get('total_pages', 0)
            })
        return forms

    @staticmethod
    def get_required_documents_for_form(form_code: str) -> List[str]:
        """Get list of required documents for a form"""
        always_required = REQUIRED_DOCUMENTS.get('always', [])

        form_specific = []
        if form_code in FORM_SCHEMAS:
            form_specific = FORM_SCHEMAS[form_code].get('required_documents', [])

        return always_required + form_specific

    @staticmethod
    def get_conditional_documents(situation: Dict) -> List[str]:
        """
        Get conditional documents based on user's situation

        Args:
            situation: Dict with keys like 'non_german', 'has_housing_costs', etc.
        """
        conditional = REQUIRED_DOCUMENTS.get('conditional', {})
        required = []

        for condition, docs in conditional.items():
            if situation.get(condition, False):
                required.extend(docs)

        return required

    @staticmethod
    def validate_date_format(date_string: str) -> bool:
        """Validate German date format DD.MM.YYYY"""
        import re
        pattern = r'^\d{2}\.\d{2}\.\d{4}$'
        return bool(re.match(pattern, date_string))

    @staticmethod
    def validate_iban(iban: str) -> bool:
        """Basic IBAN validation for Germany"""
        # Remove spaces
        iban = iban.replace(' ', '').upper()

        # Check length (German IBAN is 22 characters)
        if len(iban) != 22:
            return False

        # Check starts with DE
        if not iban.startswith('DE'):
            return False

        # Check format: DE + 2 digits + 18 alphanumeric
        import re
        pattern = r'^DE\d{20}$'
        return bool(re.match(pattern, iban))

    @staticmethod
    def get_form_completion_checklist(form_code: str) -> List[Dict]:
        """
        Generate a checklist for form completion

        Returns list of items like:
        [
            {'section': 'A', 'item': 'Personal data', 'required': True},
            ...
        ]
        """
        if form_code not in FORM_SCHEMAS:
            return []

        form = FORM_SCHEMAS[form_code]
        checklist = []

        for section_code, section_data in form.get('sections', {}).items():
            section_name = section_data.get('name', f'Section {section_code}')

            # Count fields in section
            fields = section_data.get('fields', {})
            required_count = sum(1 for f in fields.values() if f.get('required'))
            total_count = len(fields)

            checklist.append({
                'section': section_code,
                'name': section_name,
                'required_fields': required_count,
                'total_fields': total_count,
                'all_required': required_count == total_count
            })

        return checklist

    @staticmethod
    def suggest_forms_for_situation(situation: Dict) -> List[str]:
        """
        Suggest which forms user needs based on their situation

        Args:
            situation: Dict with keys like:
                - 'first_time': bool
                - 'renewal': bool
                - 'has_partner': bool
                - 'has_children': bool
                - 'has_housing_costs': bool
                - 'separated': bool
                - 'pregnant': bool

        Returns list of form codes needed
        """
        needed_forms = []

        # Main application or renewal
        if situation.get('first_time'):
            needed_forms.append('HA')
        elif situation.get('renewal'):
            needed_forms.append('WBA')

        # Always need these
        needed_forms.extend(['VM', 'EK'])

        # Conditional forms
        if situation.get('has_housing_costs'):
            needed_forms.append('KDU')

        if situation.get('has_partner') or situation.get('has_children'):
            needed_forms.append('WEP')

        if situation.get('has_children') and situation.get('children_under_15'):
            needed_forms.append('KI')

        if situation.get('separated'):
            needed_forms.append('UH1')

        if situation.get('pregnant') and not situation.get('married'):
            needed_forms.append('UH2')

        if situation.get('expensive_diet'):
            needed_forms.append('MEB')

        return list(set(needed_forms))  # Remove duplicates

    @staticmethod
    def format_form_summary(form_code: str) -> str:
        """Generate a human-readable summary of a form"""
        if form_code not in FORM_SCHEMAS:
            return f"Form {form_code} not found"

        form = FORM_SCHEMAS[form_code]

        summary = f"**{form['name']} ({form_code})**\n\n"
        summary += f"Purpose: {form['purpose']}\n"
        summary += f"Total pages: {form.get('total_pages', 'Unknown')}\n\n"

        # List sections
        sections = form.get('sections', {})
        if sections:
            summary += "**Sections:**\n"
            for code, data in sections.items():
                name = data.get('name', f'Section {code}')
                field_count = len(data.get('fields', {}))
                summary += f"- Section {code}: {name} ({field_count} fields)\n"

        # Required documents
        docs = form.get('required_documents', [])
        if docs:
            summary += "\n**Required documents:**\n"
            for doc in docs[:5]:  # Show first 5
                summary += f"- {doc}\n"
            if len(docs) > 5:
                summary += f"- ... and {len(docs) - 5} more\n"

        return summary


# Create global instance
form_utils = FormUtils()