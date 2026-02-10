from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import ImageListsOut, ImageOut
from app.models import Image, ImageLink, Title, UserTitleDetails, ImageType

async def fetch_title_images(db: AsyncSession, title_id: int, user_id: int) -> ImageListsOut:
    stmt = (
        select(Title, UserTitleDetails)
        .outerjoin(UserTitleDetails, (UserTitleDetails.title_id == Title.title_id) & (UserTitleDetails.user_id == user_id))
        .where(Title.title_id == title_id)
    )
    title_res = await db.execute(stmt)
    row = title_res.first()
    
    if not row:
        return ImageListsOut(title_id=title_id)

    title_obj, user_details = row

    # Store paths for quick comparison
    defaults = {
        title_obj.default_poster_image_path,
        title_obj.default_backdrop_image_path,
        title_obj.default_logo_image_path
    }
    user_choices = set()
    if user_details:
        user_choices = {
            user_details.chosen_poster_image_path,
            user_details.chosen_backdrop_image_path,
            user_details.chosen_logo_image_path
        }

    # Fetch all images linked to this title
    img_stmt = (
        select(Image)
        .join(ImageLink, Image.file_path == ImageLink.file_path)
        .where(ImageLink.title_id == title_id)
        .order_by(Image.vote_average.desc())
    )
    img_res = await db.execute(img_stmt)
    images = img_res.scalars().all()

    response = ImageListsOut(title_id=title_id)

    for img in images:
        img_data = ImageOut(
            file_path=img.file_path,
            type=img.type,
            width=img.width,
            height=img.height,
            iso_3166_1=img.iso_3166_1,
            iso_639_1=img.iso_639_1,
            vote_average=float(img.vote_average) if img.vote_average else 0.0,
            vote_count=img.vote_count,
            is_default=img.file_path in defaults,
            is_user_choise=img.file_path in user_choices
        )

        if img.type == ImageType.poster:
            response.posters.append(img_data)
        elif img.type == ImageType.backdrop:
            response.backdrops.append(img_data)
        elif img.type == ImageType.logo:
            response.logos.append(img_data)

    return response