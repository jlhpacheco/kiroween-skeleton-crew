"""Run the 3 demo cases: approved+paid, denied, exempt free.

    python3 demo.py
"""

from parking import PermitApplication, PermitOffice


def show(title: str, office: PermitOffice, app: PermitApplication) -> None:
    result = office.submit(app)
    print(f"\n=== {title} ===")
    print(f"Application: {result.application_id}  Status: {result.status}  Fee: ${result.fee}")
    print("Steps: " + " -> ".join(result.steps))
    for line in result.timeline:
        print(f"  - {line}")
    if result.payment:
        print(f"  Payment: {result.payment.payment_id}  ${result.payment.amount} ({result.payment.kind})")


def main() -> None:
    office = PermitOffice()

    # 1. Approved + paid — resident, good plate, allowed zone, $30 demo fee.
    show("Case 1: Approved and paid (resident, $30)",
         office,
         PermitApplication(driver="Ana Ruiz", plate="8XYZ123",
                           address="12 Pine St", zone="North Lot",
                           permit_type="resident"))

    # 2. Denied — zone is not on the allowed list. No money taken.
    show("Case 2: Denied (address outside the allowed zones)",
         office,
         PermitApplication(driver="Ben Cole", plate="4ABC99",
                           address="1 Far Away Rd", zone="Airport",
                           permit_type="visitor"))

    # 3. Exempt free — employee, $0, no payment created.
    show("Case 3: Exempt and free (employee, $0)",
         office,
         PermitApplication(driver="Cy Park", plate="7EMP001",
                           address="9 Oak Ave", zone="Downtown",
                           permit_type="employee"))

    print(f"\nPayments in the ledger: {len(office.payments)} "
          f"(case 1 only — denied and exempt create none)")


if __name__ == "__main__":
    main()
