import io
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader

from app.schemas import ReportRequest

router = APIRouter(prefix="/api", tags=["report"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))


@router.post("/report")
def generate_report(req: ReportRequest):
    # Imported lazily so the whole app doesn't fail to start if WeasyPrint's
    # system dependencies (pango/cairo) aren't installed on a given dev machine -
    # only this endpoint breaks, not the rest of the API.
    from weasyprint import HTML

    a = req.assessment
    template = env.get_template("report.html")
    html_str = template.render(
        address_label=a.input_echo.address_label,
        latitude=a.input_echo.latitude,
        longitude=a.input_echo.longitude,
        roof_area_sqm=a.input_echo.roof_area_sqm,
        roof_type=a.input_echo.roof_type.value,
        open_space_type=a.input_echo.open_space_type.value,
        open_space_area_sqm=a.input_echo.open_space_area_sqm,
        rainfall=a.rainfall,
        soil=a.soil,
        groundwater=a.groundwater,
        elevation=a.elevation,
        volume_estimate=a.volume_estimate,
        structure_recommendation=a.structure_recommendation,
        feasibility_classification=a.feasibility_classification,
        notes=a.notes,
    )

    pdf_bytes = HTML(string=html_str).write_pdf()
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=jalrakshak_report.pdf"},
    )
