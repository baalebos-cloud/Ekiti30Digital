"""Admin editing of the homepage: the hero, its images, leaders, landmarks, moments.

Every route requires a valid admin JWT. updated_by is always the verified
token's email and updated_at is set by the server; request bodies can't set
either (see app/schemas/homepage.py). Images are uploaded through the same
code as LGA images (app/api/image_uploads.py) into EKITI30/Homepage/*.

The four lists share one set of routes, built by _list_router:

    GET    /api/admin/homepage/{list}              every item, in order
    POST   /api/admin/homepage/{list}              add one at the end
    PATCH  /api/admin/homepage/{list}/{id}         edit its text
    DELETE /api/admin/homepage/{list}/{id}
    POST   /api/admin/homepage/{list}/reorder      {"ids": [...]}, every id once
    POST   /api/admin/homepage/{list}/{id}/image   upload and set its image
    DELETE /api/admin/homepage/{list}/{id}/image   back to its placeholder

where {list} is leaders, landmarks, moments or hero/images. Every write is
also logged (who, what, which id), since deletes leave no row behind.
"""

import logging

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.image_uploads import attach_uploaded_image
from app.core.auth import AdminUser, require_admin
from app.models.base import get_db
from app.models.homepage import MAX_HERO_IMAGES, HeroContent, HeroImage, Landmark, Leader, Moment
from app.schemas.homepage import (
    HeroAdminOut,
    HeroImageAdminOut,
    HeroImageCreate,
    HeroImageUpdate,
    HeroUpdate,
    LandmarkAdminOut,
    LandmarkCreate,
    LandmarkUpdate,
    LeaderAdminOut,
    LeaderCreate,
    LeaderUpdate,
    MomentAdminOut,
    MomentCreate,
    MomentUpdate,
    ReorderRequest,
)
from app.services import homepage
from app.services.cloudinary_convention import (
    HOMEPAGE_HERO_FOLDER,
    HOMEPAGE_LANDMARKS_FOLDER,
    HOMEPAGE_LEADERS_FOLDER,
    HOMEPAGE_MOMENTS_FOLDER,
)

logger = logging.getLogger(__name__)

PREFIX = "/api/admin/homepage"


def _identity(admin: AdminUser) -> str:
    return admin.email.strip().lower()


def _list_router(
    *,
    path: str,
    model: homepage.OrderedModel,
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    out_schema: type[BaseModel],
    folder: str,
    noun: str,
    max_items: int | None = None,
) -> APIRouter:
    router = APIRouter(prefix=f"{PREFIX}/{path}", tags=["admin"], dependencies=[Depends(require_admin)])

    def get_item(item_id: int, db: Session):
        item = db.get(model, item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No {noun} with id {item_id}")
        return item

    @router.get("", response_model=list[out_schema], name=f"list_{path}")
    def list_items(db: Session = Depends(get_db)):
        return homepage.ordered(db, model)

    @router.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED, name=f"create_{path}")
    def create_item(
        body: create_schema,  # type: ignore[valid-type]
        db: Session = Depends(get_db),
        admin: AdminUser = Depends(require_admin),
    ):
        if max_items is not None and db.query(model).count() >= max_items:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"There can be at most {max_items} {noun}s; delete one first",
            )
        item = model(
            **body.model_dump(),
            position=homepage.next_position(db, model),
            updated_by=_identity(admin),
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        logger.info("Admin %s added %s %s", _identity(admin), noun, item.id)
        return item

    # Declared before /{item_id} so "reorder" is never read as an id.
    @router.post("/reorder", response_model=list[out_schema], name=f"reorder_{path}")
    def reorder_items(
        body: ReorderRequest,
        db: Session = Depends(get_db),
        admin: AdminUser = Depends(require_admin),
    ):
        try:
            items = homepage.reorder(db, model, body.ids, _identity(admin))
        except homepage.InvalidOrder as err:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(err)) from None
        db.commit()
        logger.info("Admin %s reordered %ss: %s", _identity(admin), noun, body.ids)
        return items

    @router.patch("/{item_id}", response_model=out_schema, name=f"update_{path}")
    def update_item(
        item_id: int,
        body: update_schema,  # type: ignore[valid-type]
        db: Session = Depends(get_db),
        admin: AdminUser = Depends(require_admin),
    ):
        item = get_item(item_id, db)
        for name, value in body.model_dump(exclude_unset=True).items():
            setattr(item, name, value)
        item.updated_by = _identity(admin)
        db.commit()
        db.refresh(item)
        logger.info("Admin %s edited %s %s", _identity(admin), noun, item_id)
        return item

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, name=f"delete_{path}")
    def delete_item(item_id: int, db: Session = Depends(get_db), admin: AdminUser = Depends(require_admin)):
        db.delete(get_item(item_id, db))
        db.flush()
        homepage.renumber(homepage.ordered(db, model))
        db.commit()
        logger.info("Admin %s deleted %s %s", _identity(admin), noun, item_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @router.post("/{item_id}/image", response_model=out_schema, name=f"upload_{path}_image")
    async def upload_image(
        item_id: int,
        file: UploadFile = File(..., description="A JPG, PNG or WebP image"),
        db: Session = Depends(get_db),
        admin: AdminUser = Depends(require_admin),
    ):
        """Upload an image and set it as the item's image. On any failure its current image stays."""
        return await attach_uploaded_image(
            get_item(item_id, db),
            file,
            db,
            folder=folder,
            default_filename=f"{path.replace('/', '-')}-{item_id}.jpg",
            updated_by=_identity(admin),
            what=f"{noun} {item_id}",
        )

    @router.delete("/{item_id}/image", response_model=out_schema, name=f"remove_{path}_image")
    def remove_image(item_id: int, db: Session = Depends(get_db), admin: AdminUser = Depends(require_admin)):
        """Clear the item's image so it shows its placeholder again (the file stays in Cloudinary)."""
        item = get_item(item_id, db)
        item.image_url = None
        item.updated_by = _identity(admin)
        db.commit()
        db.refresh(item)
        logger.info("Admin %s removed the image from %s %s", _identity(admin), noun, item_id)
        return item

    return router


hero_images_router = _list_router(
    path="hero/images",
    model=HeroImage,
    create_schema=HeroImageCreate,
    update_schema=HeroImageUpdate,
    out_schema=HeroImageAdminOut,
    folder=HOMEPAGE_HERO_FOLDER,
    noun="hero image",
    max_items=MAX_HERO_IMAGES,
)
leaders_router = _list_router(
    path="leaders",
    model=Leader,
    create_schema=LeaderCreate,
    update_schema=LeaderUpdate,
    out_schema=LeaderAdminOut,
    folder=HOMEPAGE_LEADERS_FOLDER,
    noun="leader",
)
landmarks_router = _list_router(
    path="landmarks",
    model=Landmark,
    create_schema=LandmarkCreate,
    update_schema=LandmarkUpdate,
    out_schema=LandmarkAdminOut,
    folder=HOMEPAGE_LANDMARKS_FOLDER,
    noun="landmark",
)
moments_router = _list_router(
    path="moments",
    model=Moment,
    create_schema=MomentCreate,
    update_schema=MomentUpdate,
    out_schema=MomentAdminOut,
    folder=HOMEPAGE_MOMENTS_FOLDER,
    noun="moment",
)


# --- The hero's text (a single row) ---

hero_router = APIRouter(prefix=f"{PREFIX}/hero", tags=["admin"], dependencies=[Depends(require_admin)])


@hero_router.get("", response_model=HeroAdminOut)
def get_hero(db: Session = Depends(get_db)):
    hero = homepage.get_hero(db)
    if hero is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The hero hasn't been set up yet")
    return hero


@hero_router.patch("", response_model=HeroAdminOut)
def update_hero(body: HeroUpdate, db: Session = Depends(get_db), admin: AdminUser = Depends(require_admin)):
    """Edit the hero's text. The first save, before the hero exists, must include every field."""
    values = body.model_dump(exclude_unset=True)
    hero = homepage.get_hero(db)
    if hero is None:
        missing = sorted(set(HeroUpdate.model_fields) - set(values))
        if missing:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"The hero doesn't exist yet, so every field is needed; missing: {', '.join(missing)}",
            )
        hero = HeroContent(id=homepage.HERO_ID)
        db.add(hero)
    for name, value in values.items():
        setattr(hero, name, value)
    hero.updated_by = _identity(admin)
    db.commit()
    db.refresh(hero)
    logger.info("Admin %s edited the hero: %s", _identity(admin), ", ".join(sorted(values)))
    return hero


routers =(hero_images_router, hero_router, leaders_router, landmarks_router, moments_router)
