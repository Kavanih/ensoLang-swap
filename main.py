from fastapi import FastAPI, Query, Depends
from fastapi.responses import RedirectResponse
from schemas import Approve
import uvicorn
from enso import EnsoFinance
from dependency import new_chain

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
def borrow(chain_id: str, account: str):
    res = enso.borrow(chain_id, account)
    return res


if __name__ == "__main__":
    uvicorn.run(app=app, reload=True)
