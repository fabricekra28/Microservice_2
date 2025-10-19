from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
import httpx
import os

SERVICES = {
    "users": os.getenv("USERS_SERVICE_URL", "http://user-service:8004"),
    "maisons": os.getenv("MAISON_SERVICE_URL", "http://maison-service:8005"),
    "locations": os.getenv("LOCATION_SERVICE_URL", "http://location-service:8006"),
}

app = FastAPI(title="API Gateway App2")
templates = Jinja2Templates(directory="templates")

async def fetch_items(service):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES[service]}/{service}")
        r.raise_for_status()
        return r.json()

async def fetch_item(service, item_id):
    async with httpx.AsyncClient(timeout=10.0) as client:
        r = await client.get(f"{SERVICES[service]}/{service}/{item_id}")
        r.raise_for_status()
        return r.json()

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "services": SERVICES.keys()})

@app.get("/{service}/")
async def list_service(request: Request, service: str):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")
    items = await fetch_items(service)
    return templates.TemplateResponse("service_list.html", {"request": request, "service": service, "items": items})

@app.get("/{service}/create")
async def create_form(request: Request, service: str):
    if service not in SERVICES:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("create_form.html", {"request": request, "service": service})

@app.post("/{service}/create")
async def create_item(service: str, request: Request, name: str = Form(...), email: str = Form(None), address: str = Form(None), maison_id: int = Form(None), description: str = Form(None)):
    if service not in SERVICES:
        raise HTTPException(status_code=404)
    data = {}
    if service == "users":
        data = {"name": name, "email": email}
    elif service == "maisons":
        data = {"name": name, "address": address}
    elif service == "locations":
        data = {"maison_id": maison_id, "description": description}
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.post(f"{SERVICES[service]}/{service}", json=data)
    return RedirectResponse(f"/{service}/", status_code=303)

@app.get("/{service}/edit/{item_id}")
async def edit_form(request: Request, service: str, item_id: int):
    if service not in SERVICES:
        raise HTTPException(status_code=404)
    item = await fetch_item(service, item_id)
    return templates.TemplateResponse("edit_form.html", {"request": request, "service": service, "item": item, "item_id": item_id})

@app.post("/{service}/edit/{item_id}")
async def edit_item(service: str, item_id: int, name: str = Form(...), email: str = Form(None), address: str = Form(None), maison_id: int = Form(None), description: str = Form(None)):
    if service not in SERVICES:
        raise HTTPException(status_code=404)
    data = {}
    if service == "users":
        data = {"name": name, "email": email}
    elif service == "maisons":
        data = {"name": name, "address": address}
    elif service == "locations":
        data = {"maison_id": maison_id, "description": description}
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.put(f"{SERVICES[service]}/{service}/{item_id}", json=data)
    return RedirectResponse(f"/{service}/", status_code=303)

@app.get("/{service}/delete/{item_id}")
async def delete_item(service: str, item_id: int):
    if service not in SERVICES:
        raise HTTPException(status_code=404)
    async with httpx.AsyncClient(timeout=10.0) as client:
        await client.delete(f"{SERVICES[service]}/{service}/{item_id}")
    return RedirectResponse(f"/{service}/", status_code=303)

@app.get("/{service}/{item_id}")
async def view_item(request: Request, service: str, item_id: int):
    if service not in SERVICES:
        raise HTTPException(status_code=404)
    item = await fetch_item(service, item_id)
    return templates.TemplateResponse("item_detail.html", {"request": request, "service": service, "item": item})
