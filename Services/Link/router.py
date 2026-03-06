from fastapi import APIRouter
from fastapi.responses import RedirectResponse

from Services.Link.service import link_service
from Services.Link.schema import LinkCreate, LinkStats, LinkUpdate, LinkRead
from Shared.Config import Settings

settings = Settings()

link_router = APIRouter(prefix=f'{settings.api_prefix}/link', tags=["Link"])

@link_router.get('/shorts', name='get all shorts url')
async def get_all_shorts(link_service=link_service):
    return await link_service.all()


@link_router.get('/{short_id}', name="redirect to original url")
async def redirect_to_original(short_id: str, link_service=link_service):
    original_url = await link_service.get_original_url(short_id)
    response = RedirectResponse(original_url, status_code=302)
    response.headers["Cache-Control"] = "no-store"
    return response


@link_router.post("/shorten", name="create short url")
async def create_short_url(link_create_data: LinkCreate, link_service=link_service):
    return await link_service.create_url(link_create_data)


@link_router.get("/stats/{short_id}", name='get stats by short_id', response_model=LinkStats)
async def stats_short_id(short_id: str, link_service=link_service):
    return await link_service.get_link(short_id)


@link_router.patch("/update/{short_id}", name='update link', response_model=LinkRead)
async def update_link(short_id: str, update_data: LinkUpdate, link_service=link_service):
    return await link_service.update(short_id, update_data.model_dump())


@link_router.delete("/delete/{short_id}", name='delete link', status_code=200)
async def delete_link(short_id: str, link_service=link_service):
    return await link_service.delete(short_id)
