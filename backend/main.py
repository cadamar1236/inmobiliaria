import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import uuid

DATABASE_URL = os.environ.get("DATABASE_URL", "")
COMPANY_SLUG = os.environ.get("COMPANY_SLUG", "inmobiliaria")
db_engine = None
SessionLocal = None

class Base(DeclarativeBase):
    pass

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    db_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=db_engine)

class Propiedad(Base):
    __tablename__ = f"{COMPANY_SLUG}_propiedades"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    titulo = Column(String, nullable=False)
    descripcion = Column(Text, nullable=True)
    precio = Column(Float, nullable=False)
    moneda = Column(String, default="USD")
    tipo = Column(String, nullable=False)
    estado = Column(String, nullable=False)
    ciudad = Column(String, nullable=False)
    direccion = Column(String, nullable=True)
    habitaciones = Column(Integer, default=0)
    banos = Column(Integer, default=0)
    area_m2 = Column(Float, nullable=True)
    latitud = Column(Float, nullable=True)
    longitud = Column(Float, nullable=True)
    activo = Column(Boolean, default=True)
    fecha_publicacion = Column(DateTime, default=datetime.utcnow)
    propietario_id = Column(String, nullable=False)

class Usuario(Base):
    __tablename__ = f"{COMPANY_SLUG}_usuarios"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    telefono = Column(String, nullable=True)
    tipo = Column(String, default="comprador")
    fecha_registro = Column(DateTime, default=datetime.utcnow)

class Transaccion(Base):
    __tablename__ = f"{COMPANY_SLUG}_transacciones"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    propiedad_id = Column(String, nullable=False)
    comprador_id = Column(String, nullable=False)
    vendedor_id = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    estado = Column(String, default="pendiente")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_cierre = Column(DateTime, nullable=True)

class Imagen(Base):
    __tablename__ = f"{COMPANY_SLUG}_imagenes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    propiedad_id = Column(String, nullable=False)
    url = Column(String, nullable=False)
    descripcion = Column(String, nullable=True)
    es_principal = Column(Boolean, default=False)
    fecha_subida = Column(DateTime, default=datetime.utcnow)

class Consulta(Base):
    __tablename__ = f"{COMPANY_SLUG}_consultas"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    propiedad_id = Column(String, nullable=True)
    nombre = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefono = Column(String, nullable=True)
    mensaje = Column(Text, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    leida = Column(Boolean, default=False)

if db_engine:
    Base.metadata.create_all(bind=db_engine)

MOCK_PROPIEDADES = [
    {"id": "prop-001", "titulo": "Casa moderna en Las Condes", "descripcion": "Hermosa casa de 3 dormitorios con piscina y jardin", "precio": 450000, "moneda": "USD", "tipo": "casa", "estado": "Las Condes", "ciudad": "Santiago", "direccion": "Av. Apoquindo 1234", "habitaciones": 3, "banos": 2, "area_m2": 180, "latitud": -33.4082, "longitud": -70.5756, "activo": True, "fecha_publicacion": "2024-01-15T10:00:00", "propietario_id": "user-001"},
    {"id": "prop-002", "titulo": "Departamento en Providencia", "descripcion": "Departamento 2 dormitorios con vista panoramica", "precio": 280000, "moneda": "USD", "tipo": "departamento", "estado": "Providencia", "ciudad": "Santiago", "direccion": "Av. Nueva Providencia 567", "habitaciones": 2, "banos": 1, "area_m2": 85, "latitud": -33.4265, "longitud": -70.6082, "activo": True, "fecha_publicacion": "2024-01-20T14:30:00", "propietario_id": "user-002"},
    {"id": "prop-003", "titulo": "Terreno en Chicureo", "descripcion": "Terreno de 5000 m2 ideal para construir casa de campo", "precio": 150000, "moneda": "USD", "tipo": "terreno", "estado": "Chicureo", "ciudad": "Santiago", "direccion": "Camino a Chicureo km 12", "habitaciones": 0, "banos": 0, "area_m2": 5000, "latitud": -33.2985, "longitud": -70.6380, "activo": True, "fecha_publicacion": "2024-02-01T09:00:00", "propietario_id": "user-003"},
    {"id": "prop-004", "titulo": "Casa de playa en Reñaca", "descripcion": "Casa frente al mar con 4 dormitorios y terraza", "precio": 850000, "moneda": "USD", "tipo": "casa", "estado": "Viña del Mar", "ciudad": "Valparaíso", "direccion": "Av. Borgoño 890", "habitaciones": 4, "banos": 3, "area_m2": 250, "latitud": -32.9641, "longitud": -71.5475, "activo": True, "fecha_publicacion": "2024-02-10T11:00:00", "propietario_id": "user-001"},
    {"id": "prop-005", "titulo": "Loft en Bellavista", "descripcion": "Loft tipo estudio en el barrio mas bohemio", "precio": 120000, "moneda": "USD", "tipo": "departamento", "estado": "Bellavista", "ciudad": "Santiago", "direccion": "Pio Nono 345", "habitaciones": 1, "banos": 1, "area_m2": 45, "latitud": -33.4342, "longitud": -70.6417, "activo": True, "fecha_publicacion": "2024-02-15T16:00:00", "propietario_id": "user-004"},
    {"id": "prop-006", "titulo": "Casa colonial en La Serena", "descripcion": "Casa restaurada con patio interior y 5 dormitorios", "precio": 320000, "moneda": "USD", "tipo": "casa", "estado": "La Serena", "ciudad": "Coquimbo", "direccion": "Calle Los Naranjos 567", "habitaciones": 5, "banos": 3, "area_m2": 320, "latitud": -29.9027, "longitud": -71.2502, "activo": True, "fecha_publicacion": "2024-03-01T08:30:00", "propietario_id": "user-005"},
    {"id": "prop-007", "titulo": "Departamento en Edificio Alto", "descripcion": "Departamento de lujo con 3 dormitorios y 2 estacionamientos", "precio": 620000, "moneda": "USD", "tipo": "departamento", "estado": "Vitacura", "ciudad": "Santiago", "direccion": "Av. Vitacura 4567", "habitaciones": 3, "banos": 2, "area_m2": 140, "latitud": -33.3976, "longitud": -70.5925, "activo": True, "fecha_publicacion": "2024-03-10T13:00:00", "propietario_id": "user-002"},
    {"id": "prop-008", "titulo": "Terreno agricola en Rancagua", "descripcion": "Terreno de 10 hectareas con riego y plantaciones", "precio": 95000, "moneda": "USD", "tipo": "terreno", "estado": "Rancagua", "ciudad": "OHiggins", "direccion": "Ruta 5 Sur km 80", "habitaciones": 0, "banos": 0, "area_m2": 100000, "latitud": -34.1705, "longitud": -70.7408, "activo": True, "fecha_publicacion": "2024-03-20T10:00:00", "propietario_id": "user-006"}
]

MOCK_USUARIOS = [
    {"id": "user-001", "nombre": "Carlos Martinez", "email": "carlos@email.com", "telefono": "+56912345678", "tipo": "vendedor", "fecha_registro": "2024-01-01T00:00:00"},
    {"id": "user-002", "nombre": "Maria Gonzalez", "email": "maria@email.com", "telefono": "+56987654321", "tipo": "vendedor", "fecha_registro": "2024-01-05T00:00:00"},
    {"id": "user-003", "nombre": "Pedro Soto", "email": "pedro@email.com", "telefono": "+56923456789", "tipo": "comprador", "fecha_registro": "2024-01-10T00:00:00"},
    {"id": "user-004", "nombre": "Ana Lopez", "email": "ana@email.com", "telefono": "+56934567890", "tipo": "comprador", "fecha_registro": "2024-02-01T00:00:00"},
    {"id": "user-005", "nombre": "Jose Ramirez", "email": "jose@email.com", "telefono": "+56945678901", "tipo": "vendedor", "fecha_registro": "2024-02-15T00:00:00"},
    {"id": "user-006", "nombre": "Lucia Fernandez", "email": "lucia@email.com", "telefono": "+56956789012", "tipo": "comprador", "fecha_registro": "2024-03-01T00:00:00"}
]

MOCK_TRANSACCIONES = [
    {"id": "trans-001", "propiedad_id": "prop-002", "comprador_id": "user-003", "vendedor_id": "user-002", "monto": 280000, "estado": "completada", "fecha_creacion": "2024-02-20T10:00:00", "fecha_cierre": "2024-03-15T14:30:00"},
    {"id": "trans-002", "propiedad_id": "prop-005", "comprador_id": "user-004", "vendedor_id": "user-004", "monto": 120000, "estado": "pendiente", "fecha_creacion": "2024-03-05T09:00:00", "fecha_cierre": None},
    {"id": "trans-003", "propiedad_id": "prop-001", "comprador_id": "user-003", "vendedor_id": "user-001", "monto": 450000, "estado": "proceso", "fecha_creacion": "2024-03-10T11:00:00", "fecha_cierre": None},
    {"id": "trans-004", "propiedad_id": "prop-006", "comprador_id": "user-006", "vendedor_id": "user-005", "monto": 320000, "estado": "cancelada", "fecha_creacion": "2024-03-12T15:00:00", "fecha_cierre": "2024-03-18T10:00:00"},
    {"id": "trans-005", "propiedad_id": "prop-004", "comprador_id": "user-004", "vendedor_id": "user-001", "monto": 850000, "estado": "completada", "fecha_creacion": "2024-02-25T08:00:00", "fecha_cierre": "2024-03-20T16:00:00"}
]

MOCK_IMAGENES = [
    {"id": "img-001", "propiedad_id": "prop-001", "url": "https://images.unsplash.com/photo-1564013799919-ab600027ffc6", "descripcion": "Fachada principal", "es_principal": True, "fecha_subida": "2024-01-15T10:00:00"},
    {"id": "img-002", "propiedad_id": "prop-001", "url": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2", "descripcion": "Sala de estar", "es_principal": False, "fecha_subida": "2024-01-15T10:30:00"},
    {"id": "img-003", "propiedad_id": "prop-002", "url": "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267", "descripcion": "Vista desde el balcon", "es_principal": True, "fecha_subida": "2024-01-20T14:30:00"},
    {"id": "img-004", "propiedad_id": "prop-003", "url": "https://images.unsplash.com/photo-1500382017468-9049fed747ef", "descripcion": "Vista aerea del terreno", "es_principal": True, "fecha_subida": "2024-02-01T09:00:00"},
    {"id": "img-005", "propiedad_id": "prop-004", "url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750", "descripcion": "Frente a la playa", "es_principal": True, "fecha_subida": "2024-02-10T11:00:00"},
    {"id": "img-006", "propiedad_id": "prop-005", "url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688", "descripcion": "Interior loft", "es_principal": True, "fecha_subida": "2024-02-15T16:00:00"},
    {"id": "img-007", "propiedad_id": "prop-006", "url": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9", "descripcion": "Patio interior", "es_principal": True, "fecha_subida": "2024-03-01T08:30:00"},
    {"id": "img-008", "propiedad_id": "prop-007", "url": "https://images.unsplash.com/photo-1600566753086-00f18bb5ff5a", "descripcion": "Edificio moderno", "es_principal": True, "fecha_subida": "2024-03-10T13:00:00"}
]

MOCK_CONSULTAS = [
    {"id": "cons-001", "propiedad_id": "prop-001", "nombre": "Roberto Diaz", "email": "roberto@email.com", "telefono": "+56911122333", "mensaje": "Me interesa la propiedad, podrian agendar una visita?", "fecha_creacion": "2024-03-01T10:00:00", "leida": False},
    {"id": "cons-002", "propiedad_id": "prop-002", "nombre": "Sofia Rojas", "email": "sofia@email.com", "telefono": "+56922233444", "mensaje": "¿Tiene estacionamiento incluido?", "fecha_creacion": "2024-03-05T14:00:00", "leida": True},
    {"id": "cons-003", "propiedad_id": "prop-004", "nombre": "Diego Castro", "email": "diego@email.com", "telefono": None, "mensaje": "¿Esta disponible para visitar este fin de semana?", "fecha_creacion": "2024-03-10T09:30:00", "leida": False},
    {"id": "cons-004", "propiedad_id": "prop-006", "nombre": "Valentina Muñoz", "email": "valentina@email.com", "telefono": "+56933344555", "mensaje": "Quisiera mas informacion sobre los impuestos asociados", "fecha_creacion": "2024-03-15T11:00:00", "leida": False},
    {"id": "cons-005", "propiedad_id": None, "nombre": "Gabriel Torres", "email": "gabriel@email.com", "telefono": "+56944455666", "mensaje": "Busco propiedades en la zona oriente de Santiago, ¿tienen catalogo?", "fecha_creacion": "2024-03-20T16:00:00", "leida": True}
]

MOCK_CATEGORIAS = [
    {"id": "cat-001", "nombre": "Casas", "descripcion": "Propiedades residenciales unifamiliares", "icono": "home"},
    {"id": "cat-002", "nombre": "Departamentos", "descripcion": "Unidades en edificios residenciales", "icono": "building"},
    {"id": "cat-003", "nombre": "Terrenos", "descripcion": "Lotes y parcelas para construir", "icono": "terrain"},
    {"id": "cat-004", "nombre": "Locales comerciales", "descripcion": "Espacios para uso comercial", "icono": "store"},
    {"id": "cat-005", "nombre": "Bodegas", "descripcion": "Espacios de almacenamiento", "icono": "warehouse"}
]

MOCK_STATS = {
    "total_propiedades": len(MOCK_PROPIEDADES),
    "propiedades_activas": sum(1 for p in MOCK_PROPIEDADES if p["activo"]),
    "total_usuarios": len(MOCK_USUARIOS),
    "transacciones_completadas": sum(1 for t in MOCK_TRANSACCIONES if t["estado"] == "completada"),
    "valor_promedio_propiedades": sum(p["precio"] for p in MOCK_PROPIEDADES) / len(MOCK_PROPIEDADES),
    "consultas_pendientes": sum(1 for c in MOCK_CONSULTAS if not c["leida"])
}

app = FastAPI(title="CasaDirecta - Inmobiliaria Marketplace", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PropiedadCreate(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    precio: float
    moneda: str = "USD"
    tipo: str
    estado: str
    ciudad: str
    direccion: Optional[str] = None
    habitaciones: int = 0
    banos: int = 0
    area_m2: Optional[float] = None
    latitud: Optional[float] = None
    longitud: Optional[float] = None
    activo: bool = True
    propietario_id: str

class UsuarioCreate(BaseModel):
    nombre: str
    email: str
    telefono: Optional[str] = None
    tipo: str = "comprador"

class TransaccionCreate(BaseModel):
    propiedad_id: str
    comprador_id: str
    vendedor_id: str
    monto: float
    estado: str = "pendiente"

class ImagenCreate(BaseModel):
    propiedad_id: str
    url: str
    descripcion: Optional[str] = None
    es_principal: bool = False

class ConsultaCreate(BaseModel):
    propiedad_id: Optional[str] = None
    nombre: str
    email: str
    telefono: Optional[str] = None
    mensaje: str

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "CasaDirecta", "version": "1.0.0"}

@app.get("/api/info")
def get_info():
    return {
        "name": "CasaDirecta",
        "company": "Inmobiliaria",
        "tagline": "Compra y vende propiedades sin comision de terceros",
        "description": "Marketplace de viviendas para la venta directa entre propietarios y compradores",
        "founded": "2024",
        "team_size": 15,
        "cities_covered": ["Santiago", "Valparaíso", "Coquimbo", "OHiggins"],
        "website": "www.casadirecta.cl"
    }

@app.get("/api/metrics")
def get_metrics():
    if SessionLocal:
        db = SessionLocal()
        try:
            total_prop = db.query(Propiedad).count()
            active_prop = db.query(Propiedad).filter(Propiedad.activo == True).count()
            total_users = db.query(Usuario).count()
            completed_trans = db.query(Transaccion).filter(Transaccion.estado == "completada").count()
            avg_price = db.query(Propiedad).with_entities(Propiedad.precio).filter(Propiedad.activo == True).all()
            avg_price_val = sum(p[0] for p in avg_price) / len(avg_price) if avg_price else 0
            pending_queries = db.query(Consulta).filter(Consulta.leida == False).count()
        finally:
            db.close()
        return {
            "total_propiedades": total_prop,
            "propiedades_activas": active_prop,
            "total_usuarios": total_users,
            "transacciones_completadas": completed_trans,
            "valor_promedio_propiedades": round(avg_price_val, 2),
            "consultas_pendientes": pending_queries
        }
    return MOCK_STATS

@app.get("/api/stats")
def get_stats():
    if SessionLocal:
        db = SessionLocal()
        try:
            active = db.query(Propiedad).filter(Propiedad.activo == True).count()
            sold = db.query(Transaccion).filter(Transaccion.estado == "completada").count()
            month_trans = db.query(Transaccion).filter(Transaccion.fecha_creacion >= datetime.utcnow().replace(day=1)).count()
            return {
                "propiedades_publicadas": active,
                "transacciones_mes": month_trans,
                "transacciones_totales": sold,
                "usuarios_registrados": db.query(Usuario).count()
            }
        finally:
            db.close()
    return {
        "propiedades_publicadas": MOCK_STATS["propiedades_activas"],
        "transacciones_mes": 2,
        "transacciones_totales": MOCK_STATS["transacciones_completadas"],
        "usuarios_registrados": MOCK_STATS["total_usuarios"]
    }

@app.get("/api/recent-activity")
def get_recent_activity():
    activities = [
        {"tipo": "publicacion", "mensaje": "Nueva propiedad publicada: Casa moderna en Las Condes", "fecha": "2024-03-20T10:00:00"},
        {"tipo": "transaccion", "mensaje": "Transaccion completada: Departamento en Providencia", "fecha": "2024-03-15T14:30:00"},
        {"tipo": "consulta", "mensaje": "Nueva consulta sobre Casa de playa en Reñaca", "fecha": "2024-03-20T16:00:00"},
        {"tipo": "usuario", "mensaje": "Nuevo usuario registrado: Lucia Fernandez", "fecha": "2024-03-01T00:00:00"},
        {"tipo": "publicacion", "mensaje": "Terreno agricola en Rancagua disponible", "fecha": "2024-03-20T10:00:00"}
    ]
    return activities

@app.get("/api/chart-data")
def get_chart_data():
    return {
        "precios_promedio_por_ciudad": {
            "labels": ["Santiago", "Valparaíso", "Coquimbo", "OHiggins"],
            "datasets": [
                {
                    "label": "Precio promedio (USD)",
                    "data": [367500, 850000, 320000, 95000],
                    "backgroundColor": ["rgba(54, 162, 235, 0.2)", "rgba(255, 99, 132, 0.2)", "rgba(75, 192, 192, 0.2)", "rgba(255, 159, 64, 0.2)"],
                    "borderColor": ["rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)", "rgba(75, 192, 192, 1)", "rgba(255, 159, 64, 1)"],
                    "borderWidth": 1
                }
            ]
        },
        "transacciones_por_mes": {
            "labels": ["Enero", "Febrero", "Marzo"],
            "datasets": [
                {
                    "label": "Transacciones",
                    "data": [0, 2, 3],
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "borderColor": "rgba(75, 192, 192, 1)",
                    "borderWidth": 1
                }
            ]
        },
        "distribucion_tipos": {
            "labels": ["Casas", "Departamentos", "Terrenos"],
            "datasets": [
                {
                    "label": "Cantidad",
                    "data": [4, 3, 2],
                    "backgroundColor": ["rgba(255, 99, 132, 0.2)", "rgba(54, 162, 235, 0.2)", "rgba(255, 159, 64, 0.2)"],
                    "borderColor": ["rgba(255, 99, 132, 1)", "rgba(54, 162, 235, 1)", "rgba(255, 159, 64, 1)"],
                    "borderWidth": 1
                }
            ]
        }
    }

@app.get("/api/listings")
def get_listings(tipo: Optional[str] = None, ciudad: Optional[str] = None, precio_min: Optional[float] = None, precio_max: Optional[float] = None, habitaciones: Optional[int] = None):
    if SessionLocal:
        db = SessionLocal()
        try:
            query = db.query(Propiedad).filter(Propiedad.activo == True)
            if tipo:
                query = query.filter(Propiedad.tipo == tipo)
            if ciudad:
                query = query.filter(Propiedad.ciudad == ciudad)
            if precio_min:
                query = query.filter(Propiedad.precio >= precio_min)
            if precio_max:
                query = query.filter(Propiedad.precio <= precio_max)
            if habitaciones:
                query = query.filter(Propiedad.habitaciones == habitaciones)
            propiedades = query.all()
            return [{
                "id": p.id,
                "titulo": p.titulo,
                "descripcion": p.descripcion,
                "precio": p.precio,
                "moneda": p.moneda,
                "tipo": p.tipo,
                "estado": p.estado,
                "ciudad": p.ciudad,
                "habitaciones": p.habitaciones,
                "banos": p.banos,
                "area_m2": p.area_m2,
                "activo": p.activo,
                "fecha_publicacion": p.fecha_publicacion.isoformat() if p.fecha_publicacion else None,
                "propietario_id": p.propietario_id
            } for p in propiedades]
        finally:
            db.close()
    results = [p for p in MOCK_PROPIEDADES if p["activo"]]
    if tipo:
        results = [p for p in results if p["tipo"] == tipo]
    if ciudad:
        results = [p for p in results if p["ciudad"] == ciudad]
    if precio_min:
        results = [p for p in results if p["precio"] >= precio_min]
    if precio_max:
        results = [p for p in results if p["precio"] <= precio_max]
    if habitaciones:
        results = [p for p in results if p["habitaciones"] == habitaciones]
    return results

@app.get("/api/listings/{listing_id}")
def get_listing(listing_id: str):
    if SessionLocal:
        db = SessionLocal()
        try:
            propiedad = db.query(Propiedad).filter(Propiedad.id == listing_id).first()
            if not propiedad:
                raise HTTPException(status_code=404, detail="Propiedad no encontrada")
            imagenes = db.query(Imagen).filter(Imagen.propiedad_id == listing_id).all()
            consultas = db.query(Consulta).filter(Consulta.propiedad_id == listing_id).all()
            return {
                "propiedad": {
                    "id": propiedad.id,
                    "titulo": propiedad.titulo,
                    "descripcion": propiedad.descripcion,
                    "precio": propiedad.precio,
                    "moneda": propiedad.moneda,
                    "tipo": propiedad.tipo,
                    "estado": propiedad.estado,
                    "ciudad": propiedad.ciudad,
                    "direccion": propiedad.direccion,
                    "habitaciones": propiedad.habitaciones,
                    "banos": propiedad.banos,
                    "area_m2": propiedad.area_m2,
                    "latitud": propiedad.latitud,
                    "longitud": propiedad.longitud,
                    "activo": propiedad.activo,
                    "fecha_publicacion": propiedad.fecha_publicacion.isoformat() if propiedad.fecha_publicacion else None,
                    "propietario_id": propiedad.propietario_id
                },
                "imagenes": [{"id": i.id, "url": i.url, "descripcion": i.descripcion, "es_principal": i.es_principal} for i in imagenes],
                "consultas": [{"id": c.id, "nombre": c.nombre, "email": c.email, "mensaje": c.mensaje, "leida": c.leida} for c in consultas]
            }
        finally:
            db.close()
    propiedad = next((p for p in MOCK_PROPIEDADES if p["id"] == listing_id), None)
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    imagenes = [i for i in MOCK_IMAGENES if i["propiedad_id"] == listing_id]
    consultas = [c for c in MOCK_CONSULTAS if c["propiedad_id"] == listing_id]
    return {"propiedad": propiedad, "imagenes": imagenes, "consultas": consultas}

@app.get("/api/categories")
def get_categories():
    return MOCK_CATEGORIAS

@app.get("/api/search")
def search_listings(q: str = ""):
    if SessionLocal:
        db = SessionLocal()
        try:
            resultados = db.query(Propiedad).filter(
                Propiedad.activo == True,
                (Propiedad.titulo.ilike(f"%{q}%")) | (Propiedad.descripcion.ilike(f"%{q}%")) | (Propiedad.ciudad.ilike(f"%{q}%")) | (Propiedad.estado.ilike(f"%{q}%"))
            ).limit(20).all()
            return [{
                "id": p.id,
                "titulo": p.titulo,
                "precio": p.precio,
                "tipo": p.tipo,
                "ciudad": p.ciudad,
                "estado": p.estado,
                "habitaciones": p.habitaciones,
                "area_m2": p.area_m2
            } for p in resultados]
        finally:
            db.close()
    resultados = [p for p in MOCK_PROPIEDADES if p["activo"] and (q.lower() in p["titulo"].lower() or q.lower() in p["descripcion"].lower() or q.lower() in p["ciudad"].lower() or q.lower() in p["estado"].lower())]
    return [{"id": p["id"], "titulo": p["titulo"], "precio": p["precio"], "tipo": p["tipo"], "ciudad": p["ciudad"], "estado": p["estado"], "habitaciones": p["habitaciones"], "area_m2": p["area_m2"]} for p in resultados]

@app.get("/api/properties")
def get_properties():
    return MOCK_PROPIEDADES

@app.get("/api/properties/{property_id}")
def get_property(property_id: str):
    propiedad = next((p for p in MOCK_PROPIEDADES if p["id"] == property_id), None)
    if not propiedad:
        raise HTTPException(status_code=404, detail="Propiedad no encontrada")
    return propiedad

@app.post("/api/properties")
def create_property(property_data: PropiedadCreate):
    new_id = f"prop-{str(uuid.uuid4())[: