from fastapi import FastAPI, Query, Depends
from fastapi.responses import RedirectResponse
from schemas import Approve, Borrow, Lend
import uvicorn
from enso import EnsoFinance
from dependency import new_chain
from w3 import send_transaction, approve as approve_token

app = FastAPI()
enso = EnsoFinance()


@app.get("/")
def home():
    return RedirectResponse("/docs")


@app.get("/approve")
def approve(
    chain_id: int,
    account: str,
    token_address: str,
    amount: int,
    snapshot_id=Depends(new_chain),
):
    print(snapshot_id)
    res = enso.approve(chain_id, account, token_address, amount)
    print(res)
    return "approve"


@app.post("/borrow")
def borrow(params: Borrow, snapshot_id=Depends(new_chain)):
    print(snapshot_id)
    # print(borrow)
    res = enso.borrow(
        params.chain_id,
        params.collateral,
        params.token,
        params.from_address,
        params.amount,
    )

    return res


@app.post("/lend")
def lend(params: Lend, snapshot_id=Depends(new_chain)):
    print(params)
    res = enso.lend(params.chain_id, params.token, params.from_address, params.amount)
    return res["tx"]


if __name__ == "__main__":
    uvicorn.run(app=app, reload=True)
