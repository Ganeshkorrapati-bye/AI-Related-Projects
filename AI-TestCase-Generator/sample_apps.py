"""Built-in sample enterprise applications and their requirements.

These are curated, realistic requirement sets derived from the publicly
documented behaviour of well-known open-source enterprise applications. They let
users generate QA documentation without uploading their own document.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SampleApp:
    """A built-in enterprise application with sample requirements."""

    key: str
    name: str
    description: str
    has_api: bool
    features: tuple[str, ...]
    requirements: str


ORANGEHRM = SampleApp(
    key="orangehrm",
    name="OrangeHRM (HR Management)",
    description=(
        "Open-source Human Resource Management system covering PIM, leave, "
        "time, recruitment, performance, and admin modules."
    ),
    has_api=True,
    features=(
        "Employee login & authentication",
        "PIM - Personal Information Management",
        "Leave management & approval workflow",
        "Time & attendance tracking",
        "Recruitment & candidate pipeline",
        "Performance reviews",
        "Admin - users, roles, org structure",
        "REST API for employee and leave data",
    ),
    requirements=(
        """
OrangeHRM - Human Resource Management System
Business Requirements Specification (excerpt)

1. Authentication & Access Control
1.1 Users shall log in using a username and password over HTTPS.
1.2 After 5 consecutive failed login attempts the account shall be temporarily
    locked for 30 minutes.
1.3 The system shall support role-based access control with at least Admin and
    ESS (Employee Self Service) roles.
1.4 Sessions shall expire after 30 minutes of inactivity.

2. PIM - Personal Information Management
2.1 Admin users shall add, edit, view, and terminate employee records.
2.2 Each employee record shall include Employee ID, first/last name, job title,
    employment status, sub-unit, supervisor, and contact details.
2.3 Employee ID shall be unique across the system.
2.4 Uploaded profile photos shall be limited to 1 MB and JPG/PNG formats.

3. Leave Management
3.1 Employees shall apply for leave by selecting a leave type, start date, end
    date, and optional comment.
3.2 Leave requests shall be routed to the employee's supervisor for approval or
    rejection.
3.3 The system shall prevent applying for leave on days exceeding the available
    leave balance for the selected leave type.
3.4 Leave balances shall be calculated per leave period and per leave type.
3.5 Employees shall not apply for leave with a start date in the past.

4. Time & Attendance
4.1 Employees shall punch in and punch out to record attendance.
4.2 The system shall calculate total worked hours per timesheet period.
4.3 Timesheets shall be submitted for supervisor approval.

5. Recruitment
5.1 Recruiters shall create job vacancies and manage candidate applications.
5.2 A candidate shall move through stages: Application, Shortlist, Interview,
    Offer, Hired/Rejected.

6. REST API
6.1 The system shall expose authenticated REST endpoints to read employee and
    leave data (e.g. GET /api/v2/pim/employees, GET /api/v2/leave/leave-requests).
6.2 API access shall require OAuth2 bearer tokens.
6.3 API responses shall be JSON and return appropriate HTTP status codes.
6.4 The API shall enforce rate limiting per client.
"""
    ).strip(),
)


ERPNEXT = SampleApp(
    key="erpnext",
    name="ERPNext (ERP Suite)",
    description="Open-source ERP covering accounting, inventory, sales, and HR.",
    has_api=True,
    features=(
        "Sales order lifecycle",
        "Purchase & inventory",
        "Accounting & invoicing",
        "Stock ledger & valuation",
        "REST API (resource endpoints)",
    ),
    requirements=(
        """
ERPNext - Enterprise Resource Planning
Business Requirements Specification (excerpt)

1. Sales
1.1 Users shall create a Sales Order referencing a Customer and one or more
    Items with quantity and rate.
1.2 A Sales Order total shall equal the sum of item amounts plus taxes minus
    discounts.
1.3 A Sales Order cannot be submitted with zero items.

2. Inventory
2.1 Stock levels shall decrease when a Delivery Note is submitted.
2.2 The system shall prevent delivering more quantity than available stock when
    negative stock is disallowed.

3. Accounting
3.1 A Sales Invoice shall generate corresponding General Ledger entries.
3.2 Invoice outstanding amount shall reduce as payments are recorded.

4. REST API
4.1 The system shall expose /api/resource/{doctype} endpoints secured by API
    key/secret.
4.2 API responses shall be JSON with standard HTTP status codes.
"""
    ).strip(),
)


SALEOR = SampleApp(
    key="saleor",
    name="Saleor (E-commerce)",
    description="Open-source e-commerce platform with a rich GraphQL/REST API.",
    has_api=True,
    features=(
        "Product catalog & variants",
        "Cart & checkout",
        "Payments & orders",
        "Customer accounts",
        "API for storefront & dashboard",
    ),
    requirements=(
        """
Saleor - E-commerce Platform
Business Requirements Specification (excerpt)

1. Catalog
1.1 Products shall have variants with independent SKU, price, and stock.
1.2 Out-of-stock variants shall not be purchasable.

2. Checkout
2.1 A customer shall add items to a cart and proceed to checkout.
2.2 Checkout shall validate shipping address, shipping method, and payment.
2.3 An order shall be created only after successful payment authorization.

3. Accounts
3.1 Customers shall register, log in, and reset passwords via email.

4. API
4.1 The platform shall expose an authenticated API for catalog, checkout, and
    orders.
4.2 The API shall return appropriate error codes for invalid operations.
"""
    ).strip(),
)


SAMPLE_APPS: dict[str, SampleApp] = {
    app.key: app for app in (ORANGEHRM, ERPNEXT, SALEOR)
}


def get_sample_app(key: str) -> SampleApp | None:
    """Return a sample app by key, or ``None`` if unknown."""
    return SAMPLE_APPS.get(key)
