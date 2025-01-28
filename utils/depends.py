from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from data.models import User
from utils.token_manager import verify_jwt_token

http_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
        credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="Unauthorized")

    token = credentials.credentials
    try:
        user_credentials = verify_jwt_token(token)
        user_in_db = await User.get_or_none(id=user_credentials['user_id'])
        if not user_in_db:
            raise HTTPException(status_code=404, detail="User not found")
        return user_in_db
    except Exception as error:
        raise HTTPException(status_code=401, detail=f"Unauthorized {error}")


CurrentUser = Annotated[User, Depends(get_current_user)]
