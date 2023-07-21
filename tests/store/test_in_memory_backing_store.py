import pytest

from kiota_abstractions.store import InMemoryBackingStore

from tests.conftest import MockEntity


def test_prevents_adding_empty_keys():
    backing_store = InMemoryBackingStore()
    with pytest.raises(ValueError):
        backing_store.set("", "Samwel")
        
def test_sets_and_gets_value_from_backing_store():
    backing_store = InMemoryBackingStore()
    assert not backing_store.enumerate_()
    backing_store.set("name", "Samwel")
    assert backing_store.enumerate_() == [("name", "Samwel")]
    assert backing_store.get("name") == "Samwel"
    
def test_prevents_duplicates_in_store():
    backing_store = InMemoryBackingStore()
    assert not backing_store.enumerate_()
    backing_store.set("name", "Samwel")
    backing_store.set("name", "Samwel 2")
    assert backing_store.enumerate_() == [("name", "Samwel 2")]
    
def test_clear_backing_store():
    backing_store = InMemoryBackingStore()
    backing_store.set("name", "Sam")
    backing_store.clear()
    backing_store.get("name") is None
    assert not backing_store.enumerate_()
    
def test_return_only_changed_values():
    backing_store = InMemoryBackingStore()
    backing_store.return_only_changed_values = True
    backing_store.is_initialization_completed = False
    backing_store.set("name", "Samwel")
    assert backing_store.get("name") is None
    assert not backing_store.enumerate_()
    
    backing_store.is_initialization_completed = True
    backing_store.return_only_changed_values = True
    backing_store.set("name", "Bill")
    assert backing_store.get("name") == "Bill"
    assert backing_store.enumerate_() == [("name", "Bill")]
    
def test_enumerates_values_changed_to_none_in_store():
    backing_store = InMemoryBackingStore()
    assert not backing_store.enumerate_()
    backing_store.set("name", "Samwel")
    backing_store.set("email", "samwel@example.com")
    backing_store.set("phone", None) # remove phone
    assert backing_store.enumerate_keys_for_values_changed_to_null()
    assert backing_store.enumerate_keys_for_values_changed_to_null() == ["phone"]
    assert len(backing_store.enumerate_()) == 3
    
def test_backing_store_embedded_in_model(mock_user):
    mock_user.business_phones = ["+1 234 567 891"]
    mock_user.backing_store.return_only_changed_values = True
    changed_values = dict(mock_user.backing_store.enumerate_())
    assert len(changed_values) == 1
    assert "business_phones" in changed_values
    
def tests_backing_store_embedded_in_model_with_additonal_data_values(mock_user):
    mock_user.business_phones = ["+1 234 567 891"]
    mock_user.additional_data = {"anotherExtension": None}
    mock_user.backing_store.return_only_changed_values = True
    changed_values = dict(mock_user.backing_store.enumerate_())
    assert len(changed_values) == 2
    assert "business_phones" in changed_values
    assert "additional_data" in changed_values
    
def test_backing_store_embedded_in_model_with_collection_property_replaced_with_new_collection(mock_user):
    mock_user.business_phones = ["+1 234 567 891"]
    mock_user.backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "business_phones"
    business_phones = mock_user.backing_store.get("business_phones")
    assert business_phones == ["+1 234 567 891"]
    
def test_backing_store_embedded_in_model_with_collection_property_replaced_with_none(mock_user):
    mock_user.business_phones = None
    mock_user.backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "business_phones"
    assert changed_values[0][1] == None
    values_changed_to_null = mock_user.backing_store.enumerate_keys_for_values_changed_to_null()
    assert values_changed_to_null == ["business_phones"]
    
def test_backing_store_embedded_in_model_with_collection_property_modified_by_append(mock_user):
    mock_user.business_phones.append("+1 234 567 891")
    mock_user.backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "business_phones"
    assert len(mock_user.backing_store.get("business_phones")) == 2 # 2 items in collection as the property was modified by add
    
def test_backing_store_embedded_in_model_by_setting_nested_backed_model(mock_user):
    mock_user.manager = MockEntity(id="2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af")
    mock_user.backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "manager"
    manager = changed_values[0][1]
    assert manager.id == "2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af"
    
def test_backing_store_embedded_in_model_by_updating_nested_backed_model():
    mock_user = MockEntity(
        id="84c747c1-d2c0-410d-ba50-fc23e0b4abbe",
        manager=MockEntity(id="2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af")
    )
    mock_user.backing_store.is_initialization_completed = mock_user.manager.backing_store.is_initialization_completed = True
    mock_user.manager.business_phones = ["+1 234 567 891"]
    mock_user.backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "manager" # Backingstore should detect manager property changed
    
def test_backing_store_embedded_in_model_by_updating_nested_backed_model_returns_all_changed_nested_properties():
    mock_user = MockEntity(
        id="84c747c1-d2c0-410d-ba50-fc23e0b4abbe",
        manager=MockEntity(id="2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af")
    )
    mock_user.backing_store.is_initialization_completed = mock_user.manager.backing_store.is_initialization_completed = True
    mock_user.manager.business_phones = ["+1 234 567 891"]
    mock_user.backing_store.return_only_changed_values = True
    mock_user.manager.backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "manager" # Backingstore should detect manager property changed
    nested_changed_values = mock_user.manager.backing_store.enumerate_()
    assert len(nested_changed_values) == 1
    assert nested_changed_values[0][0] == "business_phones"
    
def test_backing_store_embedded_in_model_by_updating_nested_backed_model_collection_property():
    mock_user = MockEntity(
        id="84c747c1-d2c0-410d-ba50-fc23e0b4abbe",
        colleagues=[MockEntity(id="2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af")]
    )
    mock_user.backing_store.is_initialization_completed = mock_user.colleagues[0].backing_store.is_initialization_completed = True
    mock_user.colleagues[0].business_phones = ["+1 234 567 891"]
    mock_user.backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "colleagues" # Backingstore should detect manager property changed
    colleagues = mock_user.backing_store.get("colleagues")
    assert colleagues[0].id == "2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af"
    
def test_backing_store_embedded_in_model_by_updating_nested_backed_model_collection_property_returns_all_changed_nested_properties():
    mock_user = MockEntity(
        id="84c747c1-d2c0-410d-ba50-fc23e0b4abbe",
        colleagues=[MockEntity(id="2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af")]
    )
    mock_user.backing_store.is_initialization_completed = mock_user.colleagues[0].backing_store.is_initialization_completed = True
    mock_user.colleagues[0].business_phones = ["+1 234 567 891"]
    mock_user.backing_store.return_only_changed_values = True
    mock_user.colleagues[0].backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "colleagues" # Backingstore should detect manager property changed
    nested_changed_values = dict(mock_user.colleagues[0].backing_store.enumerate_())
    assert len(nested_changed_values) == 6
    assert "business_phones" in nested_changed_values
    
def test_backing_store_embedded_in_model_by_updating_nested_backed_model_collection_property_with_extra_value_returns_changed_nested_properties():
    mock_user = MockEntity(
        id="84c747c1-d2c0-410d-ba50-fc23e0b4abbe",
        colleagues=[MockEntity(
            id="2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af",
            business_phones=["+1 234 567 891"]
            )]
    )
    mock_user.backing_store.is_initialization_completed = mock_user.colleagues[0].backing_store.is_initialization_completed = True
    mock_user.colleagues[0].business_phones.append("+9 876 543 219")
    mock_user.backing_store.return_only_changed_values = True
    mock_user.colleagues[0].backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "colleagues" # Backingstore should detect manager property changed
    nested_changed_values = dict(mock_user.colleagues[0].backing_store.enumerate_())
    assert len(nested_changed_values) == 6
    assert "id" in nested_changed_values
    assert "business_phones" in nested_changed_values
    assert nested_changed_values["business_phones"] == (["+1 234 567 891", "+9 876 543 219"], 2)
    
def test_backing_store_embedded_in_model_by_updating_nested_backed_model_collection_property_with_extra_backed_model_returns_changed_nested_properties():
    mock_user = MockEntity(
        id="84c747c1-d2c0-410d-ba50-fc23e0b4abbe",
        colleagues=[
            MockEntity(
                id="2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af",
                business_phones=["+1 234 567 891"])
        ]
    )
    mock_user.backing_store.is_initialization_completed = mock_user.colleagues[0].backing_store.is_initialization_completed = True
    mock_user.colleagues.append(MockEntity(id="2fe22fe5-1132-42cf-90f9-1dc17e325a74"))
    mock_user.backing_store.return_only_changed_values = True
    mock_user.colleagues[0].backing_store.return_only_changed_values = True
    changed_values = mock_user.backing_store.enumerate_()
    assert len(changed_values) == 1
    assert  changed_values[0][0] == "colleagues" # Backingstore should detect colleagues property changed
    colleagues = changed_values[0][1]
    assert len(colleagues) == 2
    assert colleagues[0][0].id ==  "2f8c9b8c-8ea0-46b2-9c6d-660c9b7bf6af" # hasn't changed
    assert colleagues[0][1].id == "2fe22fe5-1132-42cf-90f9-1dc17e325a74"
    nested_changed_values = dict(mock_user.colleagues[0].backing_store.enumerate_())
    assert len(nested_changed_values) == 6
    assert "id" in nested_changed_values
    assert "business_phones" in nested_changed_values
    assert nested_changed_values["business_phones"] == (["+1 234 567 891"], 1)
    
        
        
    
    
    
    

        
