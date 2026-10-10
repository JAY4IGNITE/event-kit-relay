# PRD — Inventory & Equipment

**Module owner:** Backend
**IDs:** FR-INV-*

---

## 1. Purpose

Manage the pool of EventKits and spare equipment: kit assembly from templates,
equipment status, finding reroute candidates, and swapping faulty items.

## 2. Equipment model

- Base `Equipment` with subclasses `Camera` (resolution), `Mic` (wireless), `Tripod` (max_height_cm), `Light` (wattage).
- Status: AVAILABLE, DAMAGED, MISSING, RETIRED. Usable ⇔ AVAILABLE.
- Construction via `EquipmentFactory.create(type, **specs)` (Factory Method).
- Kit composition is template-driven: `KitTemplate.required_types()` (Abstract Factory), assembled with `EventKitBuilder` (Builder).

## 3. Functional requirements

| ID | Requirement |
|----|-------------|
| FR-INV-01 | A kit MUST be built from a `KitTemplate`; `build()` MUST raise if any required slot is unfilled. |
| FR-INV-02 | A kit is reservable only when status AVAILABLE, complete (all slots filled), and all items usable (Rule 1). |
| FR-INV-03 | `find_reroute_candidate(spec)` MUST return the first kit satisfying a composed `KitSpecification`, or None. |
| FR-INV-04 | `replace_faulty(kit, faulty)` MUST swap each faulty item with an AVAILABLE spare of the same type when possible and return success/failure. |
| FR-INV-05 | Swapping MUST mark the removed item DAMAGED/MISSING and attach the spare to the slot. |
| FR-INV-06 | Spare pool queries MUST be transactional to avoid handing one spare to two kits. |

## 4. Key operations (signatures)

```python
class EquipmentFactory:
    @staticmethod
    def create(type: EquipmentType, **specs) -> Equipment: ...

class EventKitBuilder:
    def for_template(self, t: KitTemplate) -> "EventKitBuilder": ...
    def with_item(self, item: Equipment) -> "EventKitBuilder": ...
    def build(self) -> EventKit: ...

class InventoryService:
    def find_reroute_candidate(self, spec: KitSpecification) -> Optional[EventKit]: ...
    def replace_faulty(self, kit: EventKit, faulty: list[EquipmentId]) -> bool: ...
```

## 5. Acceptance criteria

- Building a StandardAVKit without a tripod raises at `build()`.
- `replace_faulty` with a matching spare returns True and leaves the kit complete + usable.
- `replace_faulty` with no matching spare returns False and leaves the kit UNDER_MAINTENANCE.
- Two concurrent reroutes competing for the last spare: exactly one succeeds.
