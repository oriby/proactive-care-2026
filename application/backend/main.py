from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class AssessRiskInput(BaseModel):
    zipcode: str


class AssessRiskOutput(BaseModel):
    pass


class AlertInput(BaseModel):
    pass


class AlertOutput(BaseModel):
    pass


@app.post("/assess_risk")
def assess_risk(body: AssessRiskInput) -> AssessRiskOutput:
    pass


@app.post("/alert")
def alert(body: AlertInput) -> AlertOutput:
    pass