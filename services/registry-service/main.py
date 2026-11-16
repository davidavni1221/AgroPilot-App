from fastapi import FastAPI, Depends, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import date
from typing import Optional
import uuid

from sqlalchemy import Connection, delete, func, insert, select, update

from database import get_db, backend, OPERATIONAL_ERRORS, INTEGRITY_ERRORS, DATA_ERRORS
from tables import crops, emitters, farms, plots, soils
from models import Crop, Soil, Emitter, Farm, FarmCreate, FarmUpdate, Plot, PlotCreate, PlotUpdate

backend()  # נכשל בעליה אם DATABASE_URL לא תקין

app = FastAPI()

# --- מנגנון שגיאות RFC 9457 ---
class APIError(Exception):
    def __init__(self, status_code: int, code: str, title: str, detail: str):
        self.status_code = status_code
        self.code = code
        self.title = title
        self.detail = detail

# פונקציה אחת שבונה את כל תגובות השגיאה, כדי שהפורמט יהיה זהה בכל מקום
def problem_response(status_code: int, code: str, title: str, detail: str, headers: dict | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "type": "about:blank",
            "title": title,
            "status": status_code,
            "detail": detail,
            "code": code
        },
        media_type="application/problem+json",
        headers=headers,
    )

@app.exception_handler(APIError)
def api_error_handler(request: Request, exc: APIError):
    return problem_response(exc.status_code, exc.code, exc.title, exc.detail)

# שגיאות ש-FastAPI/Starlette מייצרים: נתיב לא קיים (404) או מתודה לא נתמכת (405)
@app.exception_handler(StarletteHTTPException)
def http_error_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return problem_response(404, "NOT_FOUND", "Not Found", "Route not found")
    if exc.status_code == 405:
        return problem_response(405, "VALIDATION", "Method Not Allowed", "Method not allowed on this route")
    return problem_response(exc.status_code, "VALIDATION", "Error", str(exc.detail))

# ולידציה של גוף הבקשה או הפרמטרים (Pydantic)
@app.exception_handler(RequestValidationError)
def validation_error_handler(request: Request, exc: RequestValidationError):
    details = []
    for err in exc.errors():
        field = ".".join(str(part) for part in err["loc"] if part not in ("body", "query", "path"))
        details.append(f"{field}: {err['msg']}" if field else err["msg"])
    return problem_response(422, "VALIDATION", "Unprocessable Entity", "; ".join(details))

# כשל במסד הנתונים (קובץ חסר, נעול או לא נגיש) מוחזר כ-503 עם Retry-After
def db_unavailable_handler(request: Request, exc: Exception):
    return problem_response(503, "UNAVAILABLE", "Service Unavailable", "Database is unavailable", headers={"Retry-After": "5"})

for _exc_class in OPERATIONAL_ERRORS:
    app.add_exception_handler(_exc_class, db_unavailable_handler)

for _exc_class in DATA_ERRORS:
    app.add_exception_handler(_exc_class, lambda request, exc: problem_response(422, "VALIDATION", "Unprocessable Entity", "Invalid value"))

# --- API Endpoints ---
@app.get("/health")
def health_check():
    return {"status": "ok"}

def fetch_one(db: Connection, statement) -> dict | None:
    row = db.execute(statement).mappings().first()
    return None if row is None else dict(row)

def fetch_all(db: Connection, statement) -> list[dict]:
    return [dict(row) for row in db.execute(statement).mappings()]

def exists(db: Connection, table, value) -> bool:
    return db.execute(select(table.c.id).where(table.c.id == value)).first() is not None

@app.get("/v1/crops", response_model=list[Crop])
def get_crops(db: Connection = Depends(get_db)):
    return fetch_all(db, select(crops).order_by(crops.c.id))

@app.get("/v1/crops/{id}", response_model=Crop)
def get_crop(id: str, db: Connection = Depends(get_db)):
    row = fetch_one(db, select(crops).where(crops.c.id == id))
    if not row:
        raise APIError(404, "NOT_FOUND", "Not Found", "Crop not found")
    return row

# --- Soils ---
@app.get("/v1/soils", response_model=list[Soil])
def get_soils(db: Connection = Depends(get_db)):
    return fetch_all(db, select(soils).order_by(soils.c.id))

@app.get("/v1/soils/{id}", response_model=Soil)
def get_soil(id: str, db: Connection = Depends(get_db)):
    row = fetch_one(db, select(soils).where(soils.c.id == id))
    if not row:
        raise APIError(404, "NOT_FOUND", "Not Found", "Soil not found")
    return row

# --- Emitters ---
@app.get("/v1/emitters", response_model=list[Emitter])
def get_emitters(db: Connection = Depends(get_db)):
    return fetch_all(db, select(emitters).order_by(emitters.c.id))

@app.get("/v1/emitters/{id}", response_model=Emitter)
def get_emitter(id: str, db: Connection = Depends(get_db)):
    row = fetch_one(db, select(emitters).where(emitters.c.id == id))
    if not row:
        raise APIError(404, "NOT_FOUND", "Not Found", "Emitter not found")
    return row

# --- Farms ---
@app.post("/v1/farms", response_model=Farm, status_code=201)
def create_farm(farm_in: FarmCreate, db: Connection = Depends(get_db)):
    farm_id = str(uuid.uuid4())
    db.execute(insert(farms).values(id=farm_id, name=farm_in.name))
    db.commit()
    return {"id": farm_id, "name": farm_in.name}

@app.get("/v1/farms", response_model=list[Farm])
def get_farms(db: Connection = Depends(get_db)):
    return fetch_all(db, select(farms).order_by(farms.c.id))

@app.get("/v1/farms/{id}", response_model=Farm)
def get_farm(id: str, db: Connection = Depends(get_db)):
    row = fetch_one(db, select(farms).where(farms.c.id == id))
    if not row:
        raise APIError(404, "NOT_FOUND", "Not Found", "Farm not found")
    return row

@app.patch("/v1/farms/{id}", response_model=Farm)
def update_farm(id: str, farm_in: FarmUpdate, db: Connection = Depends(get_db)):
    row = fetch_one(db, select(farms).where(farms.c.id == id))
    if not row:
        raise APIError(404, "NOT_FOUND", "Not Found", "Farm not found")

    # שם החווה חובה: אם נשלח null במפורש, זו בקשה לא תקינה (לא "אין שינוי")
    if "name" in farm_in.model_fields_set and farm_in.name is None:
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Fields cannot be null: name")

    if farm_in.name is not None:
        db.execute(update(farms).where(farms.c.id == id).values(name=farm_in.name))
        db.commit()
        return {"id": id, "name": farm_in.name}

    return row

@app.delete("/v1/farms/{id}", status_code=204, response_class=Response)
def delete_farm(id: str, db: Connection = Depends(get_db)):
    if not exists(db, farms, id):
        raise APIError(404, "NOT_FOUND", "Not Found", "Farm not found")

    plots_count = db.execute(select(func.count()).select_from(plots).where(plots.c.farm_id == id)).scalar_one()
    if plots_count > 0:
        raise APIError(409, "CONFLICT", "Conflict", "Delete a farm that still has plots")

    db.execute(delete(farms).where(farms.c.id == id))
    db.commit()

# --- Plots ---
@app.get("/v1/plots", response_model=list[Plot])
def get_plots(farm_id: Optional[str] = None, db: Connection = Depends(get_db)):
    statement = select(plots).order_by(plots.c.id)
    if farm_id:
        statement = statement.where(plots.c.farm_id == farm_id)
    return fetch_all(db, statement)

@app.get("/v1/plots/{id}", response_model=Plot)
def get_plot(id: str, db: Connection = Depends(get_db)):
    row = fetch_one(db, select(plots).where(plots.c.id == id))
    if not row:
        raise APIError(404, "NOT_FOUND", "Not Found", "Plot not found")
    return row

@app.post("/v1/plots", response_model=Plot, status_code=201)
def create_plot(plot_in: PlotCreate, db: Connection = Depends(get_db)):
    # 1. בדיקה שהתאריך אינו בעתיד
    if plot_in.planting_date > date.today():
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Planting date cannot be in the future")

    # 2. בדיקה שהחווה קיימת
    if not exists(db, farms, plot_in.farm_id):
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Unknown farm")

    # 3. בדיקה שהפריטים קיימים בקטלוגים
    if not exists(db, crops, plot_in.crop_id):
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Unknown crop")
    if not exists(db, soils, plot_in.soil_id):
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Unknown soil")
    if not exists(db, emitters, plot_in.emitter_id):
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Unknown emitter")

    # 4. בדיקה שאין חלקה באותו שם באותה חווה
    if db.execute(select(plots.c.id).where(plots.c.farm_id == plot_in.farm_id, plots.c.name == plot_in.name)).first():
        raise APIError(409, "CONFLICT", "Conflict", "Duplicate plot name on the same farm")

    # 5. שמירה במסד הנתונים
    plot_id = str(uuid.uuid4())
    try:
        db.execute(insert(plots).values(
            id=plot_id, farm_id=plot_in.farm_id, name=plot_in.name, area_m2=plot_in.area_m2,
            crop_id=plot_in.crop_id, planting_date=plot_in.planting_date.isoformat(),
            soil_id=plot_in.soil_id, row_spacing_m=plot_in.row_spacing_m,
            emitter_spacing_m=plot_in.emitter_spacing_m, emitter_id=plot_in.emitter_id,
            lat=plot_in.lat, lon=plot_in.lon,
        ))
        db.commit()
    except INTEGRITY_ERRORS:
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Invalid farm_id or constraints")

    return fetch_one(db, select(plots).where(plots.c.id == plot_id))

@app.patch("/v1/plots/{id}", response_model=Plot)
def update_plot(id: str, plot_in: PlotUpdate, db: Connection = Depends(get_db)):
    row = fetch_one(db, select(plots).where(plots.c.id == id))
    if not row:
        raise APIError(404, "NOT_FOUND", "Not Found", "Plot not found")

    update_data = plot_in.model_dump(exclude_unset=True)
    if not update_data:
        return row

    # כל השדות בחלקה חובה, לכן null אינו ערך חוקי (אחרת המסד יחזיר שגיאה ונקבל 500)
    null_fields = [key for key, value in update_data.items() if value is None]
    if null_fields:
        raise APIError(422, "VALIDATION", "Unprocessable Entity", f"Fields cannot be null: {', '.join(null_fields)}")

    if "planting_date" in update_data and update_data["planting_date"] > date.today():
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Planting date cannot be in the future")
    if "crop_id" in update_data and not exists(db, crops, update_data["crop_id"]):
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Unknown crop")
    if "soil_id" in update_data and not exists(db, soils, update_data["soil_id"]):
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Unknown soil")
    if "emitter_id" in update_data and not exists(db, emitters, update_data["emitter_id"]):
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "Unknown emitter")

    if "name" in update_data:
        duplicate = select(plots.c.id).where(plots.c.farm_id == row["farm_id"], plots.c.name == update_data["name"], plots.c.id != id)
        if db.execute(duplicate).first():
            raise APIError(409, "CONFLICT", "Conflict", "Duplicate plot name on the same farm")

    values = {key: value.isoformat() if isinstance(value, date) else value for key, value in update_data.items()}
    db.execute(update(plots).where(plots.c.id == id).values(**values))
    db.commit()

    return fetch_one(db, select(plots).where(plots.c.id == id))

@app.delete("/v1/plots/{id}", status_code=204, response_class=Response)
def delete_plot(id: str, db: Connection = Depends(get_db)):
    if not exists(db, plots, id):
        raise APIError(404, "NOT_FOUND", "Not Found", "Plot not found")

    db.execute(delete(plots).where(plots.c.id == id))
    db.commit()
