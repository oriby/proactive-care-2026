import csv
import json
from datetime import date
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_DIR = Path(__file__).resolve().parent / "data"
ALERT_DIR = Path(__file__).resolve().parent / "alerts"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Alert(BaseModel):
    title: str
    content: str


class AssessRiskInput(BaseModel):
    zipcode: str


class AssessRiskOutput(BaseModel):
    pass


class AlertInput(BaseModel):
    pass


class AlertOutput(BaseModel):
    message: str


class AllAlertsInput(BaseModel):
    pass


class AllAlertsOutput(BaseModel):
    alerts: list[Alert]


def _load_medicine_effects() -> dict[str, str]:
    effects: dict[str, str] = {}
    with open(DATA_DIR / "medicineinfo.csv", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            drug = row["drug_name"].strip()
            if drug:
                effects[drug.upper()] = row["heat_related_effects"]
    return effects


def _count_medications() -> dict[str, int]:
    with open(DATA_DIR / "patientdata.json", encoding="utf-8") as f:
        data = json.load(f)
    counts: dict[str, int] = {}
    for patient in data["patients"]:
        for med in patient["medications"]:
            counts[med] = counts.get(med, 0) + 1
    return counts


@app.post("/all_alerts")
def all_alerts(body: AllAlertsInput) -> AllAlertsOutput:
    alerts = []
    for file in sorted(ALERT_DIR.glob("*.txt")):
        alerts.append(Alert(title=file.stem, content=file.read_text(encoding="utf-8")))
    return AllAlertsOutput(alerts=alerts)


@app.post("/assess_risk")
def assess_risk(body: AssessRiskInput) -> AssessRiskOutput:
    pass


@app.post("/alert")
def alert(body: AlertInput) -> AlertOutput:
    counts = _count_medications()
    effects = _load_medicine_effects()

    lines = [
        "There is projected to be a heat wave event. Please make sure to take necessary precautions."
    ]
    for med, count in counts.items():
        key = med.upper()
        if key in effects:
            lines.append(
                f"You have {count} patients taking {med}. Patients taking this medicine may experience:\n{effects[key]}"
            )
    lines.append("If you have any questions, please consult with your medical provider.")

    message = "\n\n".join(lines)
    alert_file = ALERT_DIR / f"alert-{date.today().isoformat()}.txt"
    alert_file.write_text(message, encoding="utf-8")

    return AlertOutput(message=message)