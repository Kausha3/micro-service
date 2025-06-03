import pytest
from inventory_service import InventoryService
from models import Unit


@pytest.fixture
def inventory_service():
    """Create a fresh inventory service instance for each test."""
    return InventoryService()


def test_inventory_initialization(inventory_service):
    """Test that inventory service initializes with proper units."""
    units = inventory_service.get_all_available_units()

    # Should have multiple units
    assert len(units) > 0

    # Should have different bedroom counts
    bedroom_counts = set(unit.beds for unit in units)
    assert len(bedroom_counts) > 1

    # Should have studio units (0 bedrooms)
    assert 0 in bedroom_counts

    # Should have 1-4 bedroom units
    assert 1 in bedroom_counts
    assert 2 in bedroom_counts
    assert 3 in bedroom_counts
    assert 4 in bedroom_counts


def test_check_inventory_returns_unit_or_none(inventory_service):
    """Test that check_inventory returns a unit or None."""
    # Test with bedroom count that should have units
    result = inventory_service.check_inventory(2)

    # Should return either a Unit or None (due to randomization)
    assert result is None or isinstance(result, Unit)

    if result:
        assert result.beds == 2
        assert result.available is True


def test_check_inventory_nonexistent_bedroom_count(inventory_service):
    """Test check_inventory with bedroom count that doesn't exist."""
    # Test with bedroom count that definitely doesn't exist
    result = inventory_service.check_inventory(10)

    # Should return None
    assert result is None


def test_get_all_available_units(inventory_service):
    """Test getting all available units."""
    units = inventory_service.get_all_available_units()

    # All returned units should be available
    for unit in units:
        assert unit.available is True

    # Should have units with different characteristics
    rents = [unit.rent for unit in units]
    assert len(set(rents)) > 1  # Different rent prices

    sqfts = [unit.sqft for unit in units]
    assert len(set(sqfts)) > 1  # Different square footages


def test_reserve_unit_success(inventory_service):
    """Test successful unit reservation."""
    # Get an available unit
    available_units = inventory_service.get_all_available_units()
    assert len(available_units) > 0

    unit_to_reserve = available_units[0]
    unit_id = unit_to_reserve.unit_id

    # Reserve the unit
    result = inventory_service.reserve_unit(unit_id)

    # Should return True
    assert result is True

    # Unit should no longer be available
    updated_available_units = inventory_service.get_all_available_units()
    available_unit_ids = [unit.unit_id for unit in updated_available_units]
    assert unit_id not in available_unit_ids


def test_reserve_unit_not_found(inventory_service):
    """Test reserving a unit that doesn't exist."""
    result = inventory_service.reserve_unit("NONEXISTENT")

    # Should return False
    assert result is False


def test_reserve_unit_already_reserved(inventory_service):
    """Test reserving a unit that's already reserved."""
    # Find a unit that's already unavailable
    all_units = inventory_service.units
    unavailable_units = [unit for unit in all_units if not unit.available]

    if unavailable_units:
        unit_id = unavailable_units[0].unit_id
        result = inventory_service.reserve_unit(unit_id)

        # Should return False
        assert result is False


def test_unit_variety(inventory_service):
    """Test that units have good variety in features."""
    units = inventory_service.get_all_available_units()

    # Test rent variety
    rents = [unit.rent for unit in units]
    min_rent = min(rents)
    max_rent = max(rents)
    assert max_rent > min_rent * 1.5  # Significant rent range

    # Test square footage variety
    sqfts = [unit.sqft for unit in units]
    min_sqft = min(sqfts)
    max_sqft = max(sqfts)
    assert max_sqft > min_sqft * 2  # Significant size range

    # Test bathroom variety
    baths = [unit.baths for unit in units]
    assert len(set(baths)) > 1  # Different bathroom counts


def test_randomization_effect():
    """Test that randomization in check_inventory works over multiple calls."""
    inventory = InventoryService()

    # Make multiple calls for the same bedroom count
    results = []
    for _ in range(20):  # 20 attempts should show some variation
        result = inventory.check_inventory(2)
        results.append(result is not None)

    # With 15% chance of None, we should see some variation
    # (This test might occasionally fail due to randomness, but very rarely)
    unique_results = set(results)

    # We should see at least one True (unit found)
    assert True in unique_results


if __name__ == "__main__":
    pytest.main([__file__])
