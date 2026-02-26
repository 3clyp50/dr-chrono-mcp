"""DrChrono Healthcare UI Components.

Modular component library for clinical interfaces:
- Cards with severity indicators
- Alert banners for critical notifications
- Patient headers with demographics
- Data tables with clinical styling
- Specialized clinical lists (allergies, medications, labs)
- Appointment cards with status indicators
"""

from drchrono_mcp.ui.components.alert_banner import (
    AlertBanner,
    AlertType,
    create_critical_alert,
    create_warning_alert,
)
from drchrono_mcp.ui.components.allergy_list import (
    AllergyList,
    create_allergy_list_from_data,
)
from drchrono_mcp.ui.components.appointment_card import (
    AppointmentCard,
    AppointmentList,
    AppointmentStatus,
    create_appointment_card_from_data,
)
from drchrono_mcp.ui.components.base import (
    BaseComponent,
    Div,
    Fragment,
    RawHtml,
    Span,
)
from drchrono_mcp.ui.components.card import (
    ClinicalCard,
    Severity,
    StatCard,
)
from drchrono_mcp.ui.components.data_table import (
    CellAlignment,
    Column,
    DataTable,
    format_clinical_value,
    format_currency,
    format_date,
    format_datetime,
)
from drchrono_mcp.ui.components.lab_panel import (
    LabPanel,
    create_lab_panel_from_data,
)
from drchrono_mcp.ui.components.medication_list import (
    MedicationList,
    create_medication_list_from_data,
)
from drchrono_mcp.ui.components.patient_header import (
    PatientHeader,
    calculate_age,
    create_patient_header_from_data,
)

__all__ = [
    "BaseComponent",
    "Fragment",
    "RawHtml",
    "Div",
    "Span",
    "ClinicalCard",
    "StatCard",
    "Severity",
    "AlertBanner",
    "AlertType",
    "create_critical_alert",
    "create_warning_alert",
    "PatientHeader",
    "calculate_age",
    "create_patient_header_from_data",
    "DataTable",
    "Column",
    "CellAlignment",
    "format_date",
    "format_datetime",
    "format_currency",
    "format_clinical_value",
    "AllergyList",
    "create_allergy_list_from_data",
    "MedicationList",
    "create_medication_list_from_data",
    "LabPanel",
    "create_lab_panel_from_data",
    "AppointmentCard",
    "AppointmentList",
    "AppointmentStatus",
    "create_appointment_card_from_data",
]
