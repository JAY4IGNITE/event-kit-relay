# PRD — Deposits

**Module owner:** Backend
**IDs:** FR-DEP-*
**Pattern:** Strategy (`DepositPolicy`), driven by domain events.

---

## 1. Purpose

Model the security deposit tied to each reservation and settle it based on
return outcome. v1 models state only (no payment gateway).

## 2. States

```
PENDING --hold--> HELD --refund--> REFUNDED
                    |--forfeit(full)--> FORFEITED
                    |--forfeit(partial)--> PARTIALLY_FORFEITED
PENDING --void--> (no charge)      # when a soft hold expires before confirm
```

## 3. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-DEP-01 | A deposit MUST be created PENDING when a reservation is created. |
| FR-DEP-02 | On confirm, the deposit MUST move PENDING → HELD. |
| FR-DEP-03 | On a clean, on-time return (inspection PASS, not late), the deposit MUST be REFUNDED (Rule 15). |
| FR-DEP-04 | On damage, late return, or no-show, the deposit MUST be forfeited fully or partially per `DepositPolicy`. |
| FR-DEP-05 | On pending-hold expiry (EXPIRED), a PENDING deposit MUST be voided (never charged). |
| FR-DEP-06 | Settlement MUST be triggered by domain events, not called inline by the relay. |
| FR-DEP-07 | All forfeit amounts MUST use the `Money` value object (no floats). |

## 4. Key operations (signatures)

```python
class Deposit:
    def hold(self) -> None: ...
    def refund(self) -> None: ...
    def forfeit(self, amount: Money) -> None: ...
    def void(self) -> None: ...
    def is_refundable(self) -> bool: ...

class DepositPolicy(ABC):
    @abstractmethod
    def settle(self, reservation: Reservation, inspection: Inspection) -> list[DomainEvent]: ...

class StandardDepositPolicy(DepositPolicy): ...   # clean+on-time -> refund; else forfeit
```

## 5. Acceptance criteria

- Clean on-time return → deposit REFUNDED, `DepositRefunded` event emitted.
- Damage detected → deposit FORFEITED or PARTIALLY_FORFEITED with a `Money` amount.
- Pending hold expiry → deposit void, never HELD/FORFEITED.
