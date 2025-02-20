import pytest

@pytest.fixture()
def setUp():
    print("Launch browser")
    print("Login")
    print("Browse products")
    yield # Pause here and return control to the test function       
    print("Logoff")
    print("Close browser")

def testAddItemCart(setUp): # This test uses the fixture
    print("Add Item successful")

def testRemoveItemFromCart(setUp): # Another test using the same fixture
    print("Remove Item Successful")
