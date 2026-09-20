# Proactive Care

Date: September 20, 2026
Authors: Ori Ben Yossef, Kae Li Khoo, Hannibal Liang, Sara Wang, Scotia Rollins

## Application

The main application.

### Instructions for use

Set up the backend. From the `application/backend` folder:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Run the frontend. From the `application/frontend` folder:

```bash
npm install
npm run dev
```

Trigger an alert:

```bash
curl -X POST http://localhost:8000/alert -H "Content-Type: application/json" -d '{}'
```

## Model

A demonstration showing the machine learning model we'd implement for decision-making if we had more time.

## Notes

Source for medicine heat effect information: https://www.cdc.gov/heat-health/hcp/clinical-guidance/heat-and-medications-guidance-for-clinicians.html