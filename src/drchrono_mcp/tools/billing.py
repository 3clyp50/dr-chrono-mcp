"""Billing tools: eligibility, line items, transactions."""

from mcp.server import Server

from drchrono_mcp.clients.rest_client import DrChronoClient
from drchrono_mcp.models.types import InsuranceType


def register_billing_tools(server: Server, client: DrChronoClient) -> None:
    """Register billing tools with MCP server.

    Args:
        server: MCP Server instance
        client: DrChrono REST API client
    """

    @server.tool()
    async def drchrono_check_eligibility(
        patient_id: int,
        insurance_type: InsuranceType = "primary",
    ) -> dict:
        """Check insurance eligibility for a patient.

        Verifies patient's insurance coverage status with the payer.

        Args:
            patient_id: Patient ID (required)
            insurance_type: Which insurance to check - "primary", "secondary", or "tertiary"

        Returns:
            Eligibility status and coverage details
        """
        results = await client.check_eligibility(patient_id, insurance_type)

        if not results.get("results"):
            return {
                "patient_id": patient_id,
                "insurance_type": insurance_type,
                "has_eligibility": False,
                "message": f"No eligibility check found for {insurance_type} insurance",
            }

        # Get most recent eligibility check
        latest = results["results"][0]

        return {
            "patient_id": patient_id,
            "insurance_type": insurance_type,
            "has_eligibility": True,
            "eligibility_id": latest.get("id"),
            "status": latest.get("status"),
            "payer_name": latest.get("payer_name"),
            "subscriber_id": latest.get("subscriber_id"),
            "group_number": latest.get("group_number"),
            "coverage_active": latest.get("coverage_active"),
            "copay": latest.get("copay"),
            "deductible": latest.get("deductible"),
            "deductible_remaining": latest.get("deductible_remaining"),
            "check_date": latest.get("check_date"),
        }

    @server.tool()
    async def drchrono_get_billing_summary(
        patient_id: int,
        since: str | None = None,
        limit: int = 50,
    ) -> dict:
        """Get billing summary for a patient.

        Includes line items (charges) and recent transactions (payments).
        Calculates outstanding balance.

        Args:
            patient_id: Patient ID (required)
            since: Only include items since this date (YYYY-MM-DD)
            limit: Maximum items per category (default 50)

        Returns:
            Billing summary with charges, payments, and balance
        """
        import asyncio

        line_items, transactions = await asyncio.gather(
            client.get_line_items(patient_id=patient_id, since=since, limit=limit),
            client.get_transactions(
                since=since or "2020-01-01", patient_id=patient_id, limit=limit
            ),
        )

        # Calculate totals
        total_charges = sum(
            float(item.get("price", 0) or 0) * int(item.get("units", 1) or 1)
            for item in line_items.get("results", [])
        )
        total_payments = sum(
            float(t.get("amount", 0) or 0)
            for t in transactions.get("results", [])
            if t.get("type") == "payment"
        )
        total_adjustments = sum(
            float(t.get("amount", 0) or 0)
            for t in transactions.get("results", [])
            if t.get("type") == "adjustment"
        )

        balance = total_charges - total_payments - abs(total_adjustments)

        return {
            "patient_id": patient_id,
            "total_charges": round(total_charges, 2),
            "total_payments": round(total_payments, 2),
            "total_adjustments": round(total_adjustments, 2),
            "balance": round(balance, 2),
            "line_items": [
                {
                    "id": item["id"],
                    "procedure_code": item.get("procedure_code"),
                    "description": item.get("description"),
                    "price": item.get("price"),
                    "units": item.get("units"),
                    "service_date": item.get("service_date"),
                    "diagnosis_codes": item.get("diagnosis_codes"),
                }
                for item in line_items.get("results", [])[:20]  # Limit detail
            ],
            "recent_transactions": [
                {
                    "id": t["id"],
                    "type": t.get("type"),
                    "amount": t.get("amount"),
                    "date": t.get("posted_date"),
                    "payer": t.get("payer_name"),
                }
                for t in transactions.get("results", [])[:10]
            ],
            "line_items_count": len(line_items.get("results", [])),
            "transactions_count": len(transactions.get("results", [])),
        }

    @server.tool()
    async def drchrono_list_transactions(
        since: str,
        patient_id: int | None = None,
        limit: int = 100,
    ) -> dict:
        """List payment and adjustment transactions.

        Includes payments, refunds, and adjustments.

        Args:
            since: Start date in YYYY-MM-DD format (required)
            patient_id: Filter by patient (optional)
            limit: Maximum results (default 100, max 250)

        Returns:
            List of transactions with amounts and dates
        """
        results = await client.get_transactions(
            since=since,
            patient_id=patient_id,
            limit=min(limit, 250),
        )

        return {
            "transactions": [
                {
                    "id": t["id"],
                    "patient_id": t.get("patient"),
                    "type": t.get("type"),
                    "amount": t.get("amount"),
                    "posted_date": t.get("posted_date"),
                    "payer_name": t.get("payer_name"),
                    "check_number": t.get("check_number"),
                    "line_item": t.get("line_item"),
                }
                for t in results["results"]
            ],
            "total_count": results["total_count"],
            "has_more": results["has_more"],
        }
