from fastapi import FastAPI, Depends, Form, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from datetime import date
from typing import Annotated, Optional
import logging
import re
import uuid

import boto3
from botocore.exceptions import BotoCoreError, ClientError

from sqlalchemy import Connection, delete, func, insert, select, update

from config import get_settings
from database import get_db, backend, OPERATIONAL_ERRORS, INTEGRITY_ERRORS, DATA_ERRORS
from tables import crops, emitters, farms, plot_photos, plots, soils
from models import Crop, CropCreate, Soil, Emitter, Farm, FarmCreate, FarmSummary, FarmUpdate, Plot, PlotCreate, PlotPhoto, PlotPhotoUpload, PlotUpdate

backend()  # נכשל בעליה אם DATABASE_URL לא תקין

app = FastAPI()
logger = logging.getLogger("registry")

# --- מנגנון שגיאות RFC 9457 ---
class APIError(Exception):
    def __init__(self, status_code: int, code: str, title: str, detail: str, headers: dict | None = None):
        self.status_code = status_code
        self.code = code
        self.title = title
        self.detail = detail
        self.headers = headers

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
    return problem_response(exc.status_code, exc.code, exc.title, exc.detail, exc.headers)

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

@app.post("/v1/crops", response_model=Crop, status_code=201)
def create_crop(crop_in: CropCreate, db: Connection = Depends(get_db)):
    # The id is the name as a slug ("Sweet corn" -> "sweet-corn"), like the seeded ids.
    crop_id = re.sub(r"[^a-z0-9]+", "-", crop_in.name.lower()).strip("-")
    if not crop_id:
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "name: must contain a letter or digit (a-z, 0-9)")
    if exists(db, crops, crop_id):
        raise APIError(409, "CONFLICT", "Conflict", "A crop with this name already exists")
    db.execute(insert(crops).values(id=crop_id, **crop_in.model_dump()))
    db.commit()
    return fetch_one(db, select(crops).where(crops.c.id == crop_id))

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

@app.get("/v1/farms/{id}/summary", response_model=FarmSummary)
def get_farm_summary(id: str, db: Connection = Depends(get_db)):
    if not exists(db, farms, id):
        raise APIError(404, "NOT_FOUND", "Not Found", "Farm not found")
    row = fetch_one(db, select(
        func.count(plots.c.id).label("plot_count"),
        func.coalesce(func.sum(plots.c.area_m2), 0).label("total_area_m2"),
    ).where(plots.c.farm_id == id))
    return {"farm_id": id, **row}

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

    # The photo row points at the plot, so it goes first. The S3 object stays.
    db.execute(delete(plot_photos).where(plot_photos.c.plot_id == id))
    db.execute(delete(plots).where(plots.c.id == id))
    db.commit()

# --- Plot photos ---
PHOTO_CONTENT_TYPES = ("image/jpeg", "image/png", "image/webp")
PHOTO_MAX_BYTES = 5 * 1024 * 1024

def s3_unavailable(action: str) -> APIError:
    # Called inside an except block, so the log has the boto3 error and its traceback.
    logger.exception("S3 %s failed", action)
    return APIError(503, "UNAVAILABLE", "Service Unavailable", "Photo storage is unavailable", headers={"Retry-After": "5"})

def s3_bucket() -> str:
    bucket = get_settings().aws_s3_bucket
    if not bucket:
        logger.error("AWS_S3_BUCKET is not set")
        raise APIError(503, "UNAVAILABLE", "Service Unavailable", "Photo storage is unavailable", headers={"Retry-After": "5"})
    return bucket

def s3_client():
    # Created per request, never at import. boto3 finds the credentials by itself.
    return boto3.client("s3", region_name=get_settings().aws_region)

@app.post("/v1/plots/{id}/photo", response_model=PlotPhoto, status_code=201)
def upload_plot_photo(id: str, body: Annotated[PlotPhotoUpload, Form()], db: Connection = Depends(get_db)):
    plot = fetch_one(db, select(plots.c.farm_id).where(plots.c.id == id))
    if not plot:
        raise APIError(404, "NOT_FOUND", "Not Found", "Plot not found")

    # Every check runs before S3 is called.
    content_type = body.file.content_type
    if content_type not in PHOTO_CONTENT_TYPES:
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "file: content type must be image/jpeg, image/png or image/webp")
    data = body.file.file.read(PHOTO_MAX_BYTES + 1)
    if not data:
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "file: is empty")
    if len(data) > PHOTO_MAX_BYTES:
        raise APIError(422, "VALIDATION", "Unprocessable Entity", "file: larger than 5 MB")

    # S3 first: if it fails, the stored key is left as it was.
    key = f"{plot['farm_id']}/{id}/photo"
    bucket = s3_bucket()
    try:
        s3_client().put_object(Bucket=bucket, Key=key, Body=data, ContentType=content_type)
    except (BotoCoreError, ClientError):
        raise s3_unavailable("upload")

    # A second upload overwrites the photo.
    values = {"key": key, "content_type": content_type}
    if db.execute(select(plot_photos.c.plot_id).where(plot_photos.c.plot_id == id)).first():
        db.execute(update(plot_photos).where(plot_photos.c.plot_id == id).values(**values))
    else:
        db.execute(insert(plot_photos).values(plot_id=id, **values))
    db.commit()
    return {"plot_id": id, **values}

@app.get("/v1/plots/{id}/photo", response_class=Response)
def get_plot_photo(id: str, db: Connection = Depends(get_db)):
    if not exists(db, plots, id):
        raise APIError(404, "NOT_FOUND", "Not Found", "Plot not found")
    photo = fetch_one(db, select(plot_photos).where(plot_photos.c.plot_id == id))
    if not photo:
        raise APIError(404, "NOT_FOUND", "Not Found", "Plot has no photo")

    bucket = s3_bucket()
    try:
        obj = s3_client().get_object(Bucket=bucket, Key=photo["key"])
        data = obj["Body"].read()
    except (BotoCoreError, ClientError):
        raise s3_unavailable("download")
    return Response(content=data, media_type=photo["content_type"])
