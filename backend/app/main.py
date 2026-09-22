from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.db_models import LogRecord
from app.models import LogEvent, RawLog
from app.parser import parse_log_line
from app.analytics import get_log_summary
from app.anomaly import detect_anomalies
from app.incident_context import get_incident_logs
from app.incident_analyzer import (
    build_incident_prompt,
    analyze_incident,
)
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="TraceLens API",
    description="AI-powered application log intelligence platform",
    version="0.1.0",
)


@app.get("/")
def root():
    return {
        "name": "TraceLens",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


@app.post("/logs", response_model=LogEvent, status_code=201)
def ingest_log(
    log: RawLog,
    db: Session = Depends(get_db)
):
    try:
        parsed = parse_log_line(log.raw)

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        ) from exc

    record = LogRecord(
        timestamp=parsed.timestamp,
        level=parsed.level,
        service=parsed.service,
        message=parsed.message
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


@app.get("/logs", response_model=list[LogEvent])
def get_logs(
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return (
        db.query(LogRecord)
        .order_by(LogRecord.timestamp.desc())
        .limit(limit)
        .all()
    )

@app.get("/analytics/summary")
def analytics_summary(
    db: Session = Depends(get_db)
):
    return get_log_summary(db)

@app.get("/analytics/anomalies")
def anomalies(
    db: Session = Depends(get_db)
):
    return {
        "anomalies": detect_anomalies(db)
    }

@app.get("/incidents/context")
def incident_context(
    timestamp: str,
    db: Session = Depends(get_db)
):
    try:
        logs = get_incident_logs(
            db,
            timestamp
        )

        return {
            "anomaly_timestamp": timestamp,
            "log_count": len(logs),
            "logs": logs
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid timestamp format"
        )

@app.get("/incidents/prompt")
def incident_prompt(
    timestamp: str,
    db: Session = Depends(get_db)
):
    try:
        logs = get_incident_logs(db, timestamp)

        if not logs:
            raise HTTPException(
                status_code=404,
                detail="No logs found for this incident window"
            )

        prompt = build_incident_prompt(logs)

        return {
            "anomaly_timestamp": timestamp,
            "log_count": len(logs),
            "prompt": prompt
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid timestamp format"
        )

@app.get("/incidents/analyze")
def analyze_incident_endpoint(
    timestamp: str,
    db: Session = Depends(get_db)
):
    try:
        logs = get_incident_logs(db, timestamp)

        if not logs:
            raise HTTPException(
                status_code=404,
                detail="No logs found for this incident window"
            )

        analysis = analyze_incident(logs)

        return {
            "anomaly_timestamp": timestamp,
            "log_count": len(logs),
            "analysis": analysis
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid timestamp format"
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)