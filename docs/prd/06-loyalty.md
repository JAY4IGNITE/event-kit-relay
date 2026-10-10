# PRD — Loyalty

**Module owner:** Backend
**IDs:** FR-LOY-*
**Pattern:** Strategy (`LoyaltyPolicy`) + Observer (event subscriber).

---

## 1. Purpose

Maintain each club's loyalty score and tier from usage history, and gate
reservation eligibility. Loyalty mutation lives in an event subscriber so the
`Club` entity stays a clean aggregate root.

## 2. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-LOY-01 | A clean, on-time return MUST increase the club's score. |
| FR-LOY-02 | A late return MUST decrease the score. |
| FR-LOY-03 | Damaged equipment MUST decrease the score. |
| FR-LOY-04 | A no-show MUST decrease the score. |
| FR-LOY-05 | An expired pending hold MAY apply a small penalty (configurable; default 0). |
| FR-LOY-06 | Tier MUST be derived from score: BRONZE < SILVER < GOLD < PLATINUM (thresholds in policy). |
| FR-LOY-07 | `ClubEligibilityValidator` MUST block reservations when a club is below the eligibility threshold. |
| FR-LOY-08 | Score changes MUST be applied by a `LoyaltySubscriber` reacting to domain events, not inline. |

## 3. Key operations (signatures)

```python
class LoyaltyPolicy(ABC):
    @abstractmethod
    def delta_for(self, event: DomainEvent) -> int: ...
    @abstractmethod
    def tier_for(self, score: int) -> LoyaltyTier: ...
    @abstractmethod
    def can_reserve(self, score: int) -> bool: ...

class LoyaltySubscriber(EventSubscriber):
    def handle(self, event: DomainEvent) -> None: ...   # applies delta_for, recomputes tier
```

## 4. Acceptance criteria

- Returning clean + on-time raises score and may promote tier.
- Late/damage/no-show lowers score and may demote tier.
- A club below threshold is rejected at reservation creation with `ClubNotEligibleError`.
