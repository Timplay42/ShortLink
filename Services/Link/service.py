from fastapi import Depends, HTTPException
from sqlalchemy import select

from Services.Link.schema import LinkCreate
from Shared.DBSession import AsyncDatabase
from Shared.DBStandartFunc import BaseRepository
from Services.Link.model import Link


class LinkService(BaseRepository):
    model = Link

    async def count_redirect_count(self, model: Link):
        return await self.update(
            str(model.short_id),
            {"count_redirect": model.count_redirect+1}
        )


    async def get_link(self, short_id: str) -> Link:
        db_result = (
            await self.session.scalars(
                select(self.model)
                .where(self.model.short_id == short_id)
            )
        ).first()

        if db_result is None:
            raise HTTPException(400, "Original url not found")

        return db_result


    async def get_original_url(self, short_id: str):
        db_result = await self.get_link(short_id)

        await self.count_redirect_count(db_result)
        return db_result.original_url


    async def create_url(self, link_create_data: LinkCreate):
        for _ in range(5):
            try:
                db_result: Link = await self.create(link_create_data.model_dump())
                return db_result.short_id
            except HTTPException as error:
                detail = str(error.detail).lower()
                if error.status_code == 400 and "duplicate key value violates unique constraint" in detail:
                    continue
                raise error

        raise HTTPException(status_code=503, detail="failed to generate unique short id")



async def get_link_service(session=Depends(AsyncDatabase.get_session)):
    return LinkService(session)


link_service: LinkService = Depends(get_link_service)
