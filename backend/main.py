import os
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import uuid

PORT = int(os.environ.get("COMPANY_PORT", 8000))
DATABASE_URL = os.environ.get("DATABASE_URL", "")
COMPANY_SLUG = os.environ.get("COMPANY_SLUG", "inmodirect")
db_engine = None
SessionLocal = None

class Base(DeclarativeBase):
    pass

if DATABASE_URL:
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    db_engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=db_engine)

# SQLAlchemy Models
class PropertyModel(Base):
    __tablename__ = f"{COMPANY_SLUG}_properties"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    currency = Column(String, default="EUR")
    location = Column(String)
    property_type = Column(String)  # house, apartment, penthouse, etc.
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    square_meters = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    images = Column(Text)  # JSON array of image URLs
    features = Column(Text)  # JSON array of features
    status = Column(String, default="active")  # active, pending, sold
    user_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserModel(Base):
    __tablename__ = f"{COMPANY_SLUG}_users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    phone = Column(String)
    user_type = Column(String, default="buyer")  # buyer, seller, agent
    created_at = Column(DateTime, default=datetime.utcnow)

class ListingModel(Base):
    __tablename__ = f"{COMPANY_SLUG}_listings"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    price = Column(Float)
    listing_type = Column(String, default="sale")  # sale or rent
    is_featured = Column(Boolean, default=False)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class FavoriteModel(Base):
    __tablename__ = f"{COMPANY_SLUG}_favorites"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    property_id = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class InquiryModel(Base):
    __tablename__ = f"{COMPANY_SLUG}_inquiries"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    property_id = Column(String, nullable=False)
    user_id = Column(String)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String)
    message = Column(Text)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic Models for API
class PropertyBase(BaseModel):
    title: str
    description: Optional[str] = None
    price: float
    currency: Optional[str] = "EUR"
    location: Optional[str] = None
    property_type: Optional[str] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    square_meters: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[list] = None
    features: Optional[list] = None
    status: Optional[str] = "active"
    user_id: Optional[str] = None

class PropertyResponse(PropertyBase):
    id: str
    created_at: datetime
    updated_at: datetime

class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    phone: Optional[str] = None
    user_type: Optional[str] = "buyer"

class UserResponse(UserBase):
    id: str
    created_at: datetime

class ListingBase(BaseModel):
    property_id: str
    user_id: str
    price: Optional[float] = None
    listing_type: Optional[str] = "sale"
    is_featured: Optional[bool] = False

class ListingResponse(ListingBase):
    id: str
    created_at: datetime
    expires_at: Optional[datetime] = None

class FavoriteBase(BaseModel):
    user_id: str
    property_id: str

class FavoriteResponse(FavoriteBase):
    id: str
    created_at: datetime

class InquiryBase(BaseModel):
    property_id: str
    user_id: Optional[str] = None
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None

class InquiryResponse(InquiryBase):
    id: str
    is_read: bool
    created_at: datetime

# Mock Data
MOCK_PROPERTIES = [
    {
        "id": "prop-001",
        "title": "Modern Apartment in City Center",
        "description": "Beautiful 3-bedroom apartment with panoramic views. Recently renovated with high-end finishes.",
        "price": 350000.0,
        "currency": "EUR",
        "location": "Madrid, Centro",
        "property_type": "apartment",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_meters": 120.0,
        "latitude": 40.4168,
        "longitude": -3.7038,
        "images": ["https://images.unsplash.com/photo-1522708323590-d24dbb7b0e9e"],
        "features": ["elevator", "parking", "terrace", "pool"],
        "status": "active",
        "user_id": "user-001",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "prop-002",
        "title": "Cozy Studio near University",
        "description": "Perfect for students or young professionals. Fully furnished studio with modern amenities.",
        "price": 120000.0,
        "currency": "EUR",
        "location": "Barcelona, Gràcia",
        "property_type": "studio",
        "bedrooms": 1,
        "bathrooms": 1,
        "square_meters": 45.0,
        "latitude": 41.3874,
        "longitude": 2.1686,
        "images": ["https://images.unsplash.com/photo-1502672260266-1c1ef2d93688"],
        "features": ["furnished", "wifi", "air_conditioning"],
        "status": "active",
        "user_id": "user-002",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "prop-003",
        "title": "Luxury Villa with Sea Views",
        "description": "Stunning 5-bedroom villa with infinity pool and direct sea access. Private garden and garage.",
        "price": 1250000.0,
        "currency": "EUR",
        "location": "Marbella, Puerto Banús",
        "property_type": "villa",
        "bedrooms": 5,
        "bathrooms": 4,
        "square_meters": 350.0,
        "latitude": 36.5101,
        "longitude": -4.8824,
        "images": ["https://images.unsplash.com/photo-1564013799919-ab600027ffc6"],
        "features": ["pool", "garden", "garage", "sea_view", "security"],
        "status": "active",
        "user_id": "user-003",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "prop-004",
        "title": "Commercial Space in Business District",
        "description": "Prime location commercial space perfect for retail or office. High foot traffic area.",
        "price": 580000.0,
        "currency": "EUR",
        "location": "Valencia, Ciutat Vella",
        "property_type": "commercial",
        "bedrooms": 0,
        "bathrooms": 2,
        "square_meters": 200.0,
        "latitude": 39.4699,
        "longitude": -0.3763,
        "images": ["https://images.unsplash.com/photo-1497366216548-37526070297c"],
        "features": ["showroom", "storage", "air_conditioning"],
        "status": "active",
        "user_id": "user-001",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "prop-005",
        "title": "Charming Townhouse with Garden",
        "description": "Traditional townhouse beautifully restored. Features original wooden beams and private garden.",
        "price": 450000.0,
        "currency": "EUR",
        "location": "Seville, Santa Cruz",
        "property_type": "house",
        "bedrooms": 4,
        "bathrooms": 3,
        "square_meters": 180.0,
        "latitude": 37.3891,
        "longitude": -5.9845,
        "images": ["https://images.unsplash.com/photo-1600596542815-ffad4c1539a9"],
        "features": ["garden", "fireplace", "terrace", "patio"],
        "status": "active",
        "user_id": "user-004",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "prop-006",
        "title": "Beachfront Penthouse",
        "description": "Exclusive penthouse with direct beach access. Breathtaking sunset views from private terrace.",
        "price": 890000.0,
        "currency": "EUR",
        "location": "Benidorm, Playa Levante",
        "property_type": "penthouse",
        "bedrooms": 3,
        "bathrooms": 2,
        "square_meters": 150.0,
        "latitude": 38.5409,
        "longitude": -0.1310,
        "images": ["https://images.unsplash.com/photo-1600607687939-ce8a6c25118c"],
        "features": ["sea_view", "terrace", "pool", "garage", "doorman"],
        "status": "active",
        "user_id": "user-005",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "prop-007",
        "title": "Affordable Flat for First Buyers",
        "description": "Great opportunity for first-time buyers. Well-maintained 2-bedroom flat in quiet neighborhood.",
        "price": 185000.0,
        "currency": "EUR",
        "location": "Bilbao, Deusto",
        "property_type": "apartment",
        "bedrooms": 2,
        "bathrooms": 1,
        "square_meters": 80.0,
        "latitude": 43.2630,
        "longitude": -2.9350,
        "images": ["https://images.unsplash.com/photo-1560448204-e02f11c3d0e2"],
        "features": ["elevator", "balcony", "storage_room"],
        "status": "active",
        "user_id": "user-002",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    },
    {
        "id": "prop-008",
        "title": "Historic Loft in Old Town",
        "description": "Converted industrial loft in historic building. High ceilings and original brick walls.",
        "price": 320000.0,
        "currency": "EUR",
        "location": "Granada, Albaicín",
        "property_type": "loft",
        "bedrooms": 2,
        "bathrooms": 1,
        "square_meters": 100.0,
        "latitude": 37.1773,
        "longitude": -3.5986,
        "images": ["https://images.unsplash.com/photo-1600607687644-c7171b42460b"],
        "features": ["high_ceilings", "exposed_brick", "roof_terrace"],
        "status": "active",
        "user_id": "user-003",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
]

MOCK_USERS = [
    {"id": "user-001", "email": "carlos.garcia@email.com", "name": "Carlos García", "phone": "+34 612 345 678", "user_type": "seller", "created_at": datetime.now()},
    {"id": "user-002", "email": "ana.lopez@email.com", "name": "Ana López", "phone": "+34 623 456 789", "user_type": "buyer", "created_at": datetime.now()},
    {"id": "user-003", "email": "miguel.sanchez@email.com", "name": "Miguel Sánchez", "phone": "+34 634 567 890", "user_type": "seller", "created_at": datetime.now()},
    {"id": "user-004", "email": "laura.martinez@email.com", "name": "Laura Martínez", "phone": "+34 645 678 901", "user_type": "buyer", "created_at": datetime.now()},
    {"id": "user-005", "email": "javier.rodriguez@email.com", "name": "Javier Rodríguez", "phone": "+34 656 789 012", "user_type": "agent", "created_at": datetime.now()}
]

MOCK_LISTINGS = [
    {"id": "list-001", "property_id": "prop-001", "user_id": "user-001", "price": 350000.0, "listing_type": "sale", "is_featured": True, "created_at": datetime.now(), "expires_at": None},
    {"id": "list-002", "property_id": "prop-002", "user_id": "user-002", "price": 120000.0, "listing_type": "sale", "is_featured": False, "created_at": datetime.now(), "expires_at": None},
    {"id": "list-003", "property_id": "prop-003", "user_id": "user-003", "price": 1250000.0, "listing_type": "sale", "is_featured": True, "created_at": datetime.now(), "expires_at": None},
    {"id": "list-004", "property_id": "prop-004", "user_id": "user-001", "price": 580000.0, "listing_type": "sale", "is_featured": False, "created_at": datetime.now(), "expires_at": None},
    {"id": "list-005", "property_id": "prop-005", "user_id": "user-004", "price": 450000.0, "listing_type": "sale", "is_featured": False, "created_at": datetime.now(), "expires_at": None},
    {"id": "list-006", "property_id": "prop-006", "user_id": "user-005", "price": 890000.0, "listing_type": "sale", "is_featured": True, "created_at": datetime.now(), "expires_at": None},
    {"id": "list-007", "property_id": "prop-007", "user_id": "user-002", "price": 185000.0, "listing_type": "sale", "is_featured": False, "created_at": datetime.now(), "expires_at": None},
    {"id": "list-008", "property_id": "prop-008", "user_id": "user-003", "price": 320000.0, "listing_type": "sale", "is_featured": False, "created_at": datetime.now(), "expires_at": None}
]

MOCK_FAVORITES = [
    {"id": "fav-001", "user_id": "user-002", "property_id": "prop-001", "created_at": datetime.now()},
    {"id": "fav-002", "user_id": "user-004", "property_id": "prop-003", "created_at": datetime.now()},
    {"id": "fav-003", "user_id": "user-002", "property_id": "prop-006", "created_at": datetime.now()},
    {"id": "fav-004", "user_id": "user-004", "property_id": "prop-008", "created_at": datetime.now()},
    {"id": "fav-005", "user_id": "user-002", "property_id": "prop-005", "created_at": datetime.now()}
]

MOCK_INQUIRIES = [
    {"id": "inq-001", "property_id": "prop-001", "user_id": "user-002", "name": "Ana López", "email": "ana.lopez@email.com", "phone": "+34 623 456 789", "message": "I'm interested in visiting this property. Is it available this weekend?", "is_read": False, "created_at": datetime.now()},
    {"id": "inq-002", "property_id": "prop-003", "user_id": "user-004", "name": "Laura Martínez", "email": "laura.martinez@email.com", "phone": "+34 645 678 901", "message": "Could you provide more information about the pool and garden maintenance?", "is_read": True, "created_at": datetime.now()},
    {"id": "inq-003", "property_id": "prop-006", "user_id": None, "name": "Pedro Ruiz", "email": "pedro.ruiz@email.com", "phone": "+34 667 890 123", "message": "Is the penthouse still available? I would like to schedule a viewing.", "is_read": False, "created_at": datetime.now()},
    {"id": "inq-004", "property_id": "prop-001", "user_id": "user-004", "name": "Laura Martínez", "email": "laura.martinez@email.com", "phone": "+34 645 678 901", "message": "Does the apartment include parking space?", "is_read": False, "created_at": datetime.now()},
    {"id": "inq-005", "property_id": "prop-008", "user_id": "user-002", "name": "Ana López", "email": "ana.lopez@email.com", "phone": "+34 623 456 789", "message": "I love this loft! Are pets allowed in the building?", "is_read": True, "created_at": datetime.now()}
]

app = FastAPI(title="InmoDirect API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database helper
def get_db():
    if SessionLocal:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    else:
        yield None

# Create tables on startup
@app.on_event("startup")
async def startup():
    if db_engine:
        Base.metadata.create_all(bind=db_engine)

# Helper functions
def get_mock_property(property_id: str):
    for p in MOCK_PROPERTIES:
        if p["id"] == property_id:
            return p
    return None

def get_mock_listing(listing_id: str):
    for l in MOCK_LISTINGS:
        if l["id"] == listing_id:
            return l
    return None

def get_mock_user(user_id: str):
    for u in MOCK_USERS:
        if u["id"] == user_id:
            return u
    return None

# Health endpoint
@app.get("/health")
async def health():
    return {"status": "ok", "app": "InmoDirect", "version": "1.0.0"}

# Company info
@app.get("/api/info")
async def info():
    return {
        "name": "InmoDirect",
        "tagline": "Vende tu vivienda sin comisiones de terceros",
        "description": "Marketplace de viviendas para la venta directa entre propietarios y compradores, sin intermediarios ni comisiones.",
        "founded": "2024",
        "team_size": 25,
        "headquarters": "Madrid, Spain",
        "mission": "Eliminar las barreras y costes innecesarios en la compraventa de viviendas, conectando directamente a propietarios e interesados.",
        "regions": ["Madrid", "Barcelona", "Valencia", "Sevilla", "Málaga", "Bilbao"],
        "total_listings": 8500,
        "active_users": 45000,
        "avg_price": 425000
    }

# Metrics endpoint
@app.get("/api/metrics")
async def metrics():
    return {
        "total_properties": 8500,
        "active_listings": 7200,
        "new_listings_this_month": 340,
        "properties_sold_this_month": 89,
        "total_users": 45000,
        "buyers": 32000,
        "sellers": 12000,
        "agents": 1000,
        "average_days_on_market": 45,
        "average_price_per_sqm": 2850,
        "total_inquiries": 12300,
        "conversation_rate": 0.23,
        "favorites_count": 9800,
        "monthly_active_users": 12500,
        "revenue_saved_by_users": 42000000,
        "satisfaction_rate": 0.94
    }

# Properties endpoints
@app.get("/api/properties")
async def get_properties(
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    property_type: Optional[str] = Query(None),
    bedrooms: Optional[int] = Query(None),
    location: Optional[str] = Query(None),
    status: Optional[str] = Query("active")
):
    if SessionLocal:
        db = SessionLocal()
        try:
            query = db.query(PropertyModel).filter(PropertyModel.status == status)
            if min_price:
                query = query.filter(PropertyModel.price >= min_price)
            if max_price:
                query = query.filter(PropertyModel.price <= max_price)
            if property_type:
                query = query.filter(PropertyModel.property_type == property_type)
            if bedrooms:
                query = query.filter(PropertyModel.bedrooms >= bedrooms)
            if location:
                query = query.filter(PropertyModel.location.ilike(f"%{location}%"))
            properties = query.all()
            result = []
            for p in properties:
                result.append({
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "price": p.price,
                    "currency": p.currency,
                    "location": p.location,
                    "property_type": p.property_type,
                    "bedrooms": p.bedrooms,
                    "bathrooms": p.bathrooms,
                    "square_meters": p.square_meters,
                    "latitude": p.latitude,
                    "longitude": p.longitude,
                    "images": p.images,
                    "features": p.features,
                    "status": p.status,
                    "user_id": p.user_id,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at
                })
            db.close()
            return {"properties": result, "total": len(result)}
        except:
            db.close()
    
    # Mock fallback
    filtered = []
    for p in MOCK_PROPERTIES:
        if p["status"] != status:
            continue
        if min_price and p["price"] < min_price:
            continue
        if max_price and p["price"] > max_price:
            continue
        if property_type and p["property_type"] != property_type:
            continue
        if bedrooms and p["bedrooms"] < bedrooms:
            continue
        if location and location.lower() not in p["location"].lower():
            continue
        filtered.append(p)
    return {"properties": filtered, "total": len(filtered)}

@app.get("/api/properties/{property_id}")
async def get_property(property_id: str):
    if SessionLocal:
        db = SessionLocal()
        try:
            p = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
            db.close()
            if p:
                return {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "price": p.price,
                    "currency": p.currency,
                    "location": p.location,
                    "property_type": p.property_type,
                    "bedrooms": p.bedrooms,
                    "bathrooms": p.bathrooms,
                    "square_meters": p.square_meters,
                    "latitude": p.latitude,
                    "longitude": p.longitude,
                    "images": p.images,
                    "features": p.features,
                    "status": p.status,
                    "user_id": p.user_id,
                    "created_at": p.created_at,
                    "updated_at": p.updated_at
                }
            raise HTTPException(status_code=404, detail="Property not found")
        except:
            db.close()
    
    p = get_mock_property(property_id)
    if p:
        return p
    raise HTTPException(status_code=404, detail="Property not found")

@app.post("/api/properties")
async def create_property(property_data: PropertyBase):
    property_id = f"prop-{uuid.uuid4().hex[:8]}"
    
    if SessionLocal:
        db = SessionLocal()
        try:
            new_property = PropertyModel(
                id=property_id,
                title=property_data.title,
                description=property_data.description,
                price=property_data.price,
                currency=property_data.currency or "EUR",
                location=property_data.location,
                property_type=property_data.property_type,
                bedrooms=property_data.bedrooms,
                bathrooms=property_data.bathrooms,
                square_meters=property_data.square_meters,
                latitude=property_data.latitude,
                longitude=property_data.longitude,
                images=str(property_data.images) if property_data.images else None,
                features=str(property_data.features) if property_data.features else None,
                status=property_data.status or "active",
                user_id=property_data.user_id
            )
            db.add(new_property)
            db.commit()
            db.refresh(new_property)
            result = {
                "id": new_property.id,
                "title": new_property.title,
                "description": new_property.description,
                "price": new_property.price,
                "currency": new_property.currency,
                "location": new_property.location,
                "property_type": new_property.property_type,
                "bedrooms": new_property.bedrooms,
                "bathrooms": new_property.bathrooms,
                "square_meters": new_property.square_meters,
                "latitude": new_property.latitude,
                "longitude": new_property.longitude,
                "images": new_property.images,
                "features": new_property.features,
                "status": new_property.status,
                "user_id": new_property.user_id,
                "created_at": new_property.created_at,
                "updated_at": new_property.updated_at
            }
            db.close()
            return result
        except Exception as e:
            db.rollback()
            db.close()
            raise HTTPException(status_code=400, detail=str(e))
    
    # Mock fallback
    new_property = {
        "id": property_id,
        "title": property_data.title,
        "description": property_data.description,
        "price": property_data.price,
        "currency": property_data.currency or "EUR",
        "location": property_data.location,
        "property_type": property_data.property_type,
        "bedrooms": property_data.bedrooms,
        "bathrooms": property_data.bathrooms,
        "square_meters": property_data.square_meters,
        "latitude": property_data.latitude,
        "longitude": property_data.longitude,
        "images": property_data.images,
        "features": property_data.features,
        "status": property_data.status or "active",
        "user_id": property_data.user_id,
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    MOCK_PROPERTIES.append(new_property)
    return new_property

@app.put("/api/properties/{property_id}")
async def update_property(property_id: str, property_data: PropertyBase):
    if SessionLocal:
        db = SessionLocal()
        try:
            p = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
            if not p:
                db.close()
                raise HTTPException(status_code=404, detail="Property not found")
            
            p.title = property_data.title
            p.description = property_data.description
            p.price = property_data.price
            p.currency = property_data.currency or "EUR"
            p.location = property_data.location
            p.property_type = property_data.property_type
            p.bedrooms = property_data.bedrooms
            p.bathrooms = property_data.bathrooms
            p.square_meters = property_data.square_meters
            p.latitude = property_data.latitude
            p.longitude = property_data.longitude
            p.images = str(property_data.images) if property_data.images else None
            p.features = str(property_data.features) if property_data.features else None
            p.status = property_data.status or "active"
            p.user_id = property_data.user_id
            p.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(p)
            result = {
                "id": p.id,
                "title": p.title,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "location": p.location,
                "property_type": p.property_type,
                "bedrooms": p.bedrooms,
                "bathrooms": p.bathrooms,
                "square_meters": p.square_meters,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "images": p.images,
                "features": p.features,
                "status": p.status,
                "user_id": p.user_id,
                "created_at": p.created_at,
                "updated_at": p.updated_at
            }
            db.close()
            return result
        except Exception as e:
            db.rollback()
            db.close()
            raise HTTPException(status_code=400, detail=str(e))
    
    # Mock fallback
    p = get_mock_property(property_id)
    if not p:
        raise HTTPException(status_code=404, detail="Property not found")
    
    p["title"] = property_data.title
    p["description"] = property_data.description
    p["price"] = property_data.price
    p["currency"] = property_data.currency or "EUR"
    p["location"] = property_data.location
    p["property_type"] = property_data.property_type
    p["bedrooms"] = property_data.bedrooms
    p["bathrooms"] = property_data.bathrooms
    p["square_meters"] = property_data.square_meters
    p["latitude"] = property_data.latitude
    p["longitude"] = property_data.longitude
    p["images"] = property_data.images
    p["features"] = property_data.features
    p["status"] = property_data.status or "active"
    p["user_id"] = property_data.user_id
    p["updated_at"] = datetime.now()
    return p

@app.delete("/api/properties/{property_id}")
async def delete_property(property_id: str):
    if SessionLocal:
        db = SessionLocal()
        try:
            p = db.query(PropertyModel).filter(PropertyModel.id == property_id).first()
            if not p:
                db.close()
                raise HTTPException(status_code=404, detail="Property not found")
            db.delete(p)
            db.commit()
            db.close()
            return {"message": "Property deleted successfully"}
        except:
            db.close()
    
    # Mock fallback
    for i, p in enumerate(MOCK_PROPERTIES):
        if p["id"] == property_id:
            MOCK_PROPERTIES.pop(i)
            return {"message": "Property deleted successfully"}
    raise HTTPException(status_code=404, detail="Property not found")

# Users endpoints
@app.get("/api/users")
async def get_users(user_type: Optional[str] = Query(None)):
    if SessionLocal:
        db = SessionLocal()
        try:
            query = db.query(UserModel)
            if user_type:
                query = query.filter(UserModel.user_type == user_type)
            users = query.all()
            result = []
            for u in users:
                result.append({
                    "id": u.id,
                    "email": u.email,
                    "name": u.name,
                    "phone": u.phone,
                    "user_type": u.user_type,
                    "created_at": u.created_at
                })
            db.close()
            return {"users": result, "total": len(result)}
        except:
            db.close()
    
    if user_type:
        filtered = [u for u in MOCK_USERS if u["user_type"] == user_type]
    else:
        filtered = MOCK_USERS
    return {"users": filtered, "total": len(filtered)}

@app.get("/api/users/{user_id}")
async def get_user(user_id: str):
    if SessionLocal:
        db = SessionLocal()
        try:
            u = db.query(UserModel).filter(UserModel.id == user_id).first()
            db.close()
            if u:
                return {
                    "id": u.id,
                    "email": u.email,
                    "name": u.name,
                    "phone": u.phone,
                    "user_type": u.user_type,
                    "created_at": u.created_at
                }
            raise HTTPException(status_code=404, detail="User not found")
        except:
            db.close()
    
    u = get_mock_user(user_id)
    if u:
        return u
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/api/users")
async def create_user(user_data: UserBase):
    user_id = f"user-{uuid.uuid4().hex[:8]}"
    
    if SessionLocal:
        db = SessionLocal()
        try:
            new_user = UserModel(
                id=user_id,
                email=user_data.email,
                name=user_data.name,
                phone=user_data.phone,
                user_type=user_data.user_type or "buyer"
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            result = {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "phone": new_user.phone,
                "user_type": new_user.user_type,
                "created_at": new_user.created_at
            }
            db.close()
            return result
        except Exception as e:
            db.rollback()
            db.close()
            raise HTTPException(status_code=400,