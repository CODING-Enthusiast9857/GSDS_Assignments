import pytest

from wallet import wallet

def test_default_initial_amount():
    wall=wallet()
    assert wall.balance==0
    
def test_add_cash():
    wall=wallet(10)
    wall.add_cash(90)
    assert wall.balance==100
    
def test_spend_cash():
    wall=wallet(20)
    wall.spend_cash(10)
    assert wall.balance==10
    
def test_wallet_spend_cash_raises_exception_on_insufficient_amount():
    wall = wallet()
    #with pytest.raises(InsufficientAmount):
    wall.spend_cash(100)
    assert wall.balance==0