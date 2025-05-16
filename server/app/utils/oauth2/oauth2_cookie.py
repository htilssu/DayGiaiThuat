from typing import Any, Dict, cast
from typing import Optional

from fastapi import HTTPException, Request
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.oauth2 import OAuth2
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.config import settings


class OAuth2PasswordCookie(OAuth2):
    """
    OAuth2 flow cho xác thực sử dụng bearer token từ cookie.
    :argument tokenUrl: URL để lấy token OAuth2 (đường dẫn đến path operation)
    :argument scheme_name: Tên của scheme bảo mật trong OpenAPI
    :argument scopes: Các scopes OAuth2 được yêu cầu
    :argument description: Mô tả scheme bảo mật trong OpenAPI
    :argument auto_error: Tự động báo lỗi khi không tìm thấy token
    :argument cookie_name: Tên của cookie chứa token, mặc định lấy từ settings
    """

    def __init__(
            self,
            tokenUrl: str,
            scheme_name: Optional[str] = None,
            scopes: Optional[Dict[str, str]] = None,
            description: Optional[str] = None,
            auto_error: bool = True,
            cookie_name: Optional[str] = None,
    ):
        """
        Khởi tạo OAuth2PasswordCookie.
        
        Args:
            tokenUrl (str): URL để lấy token OAuth2 (đường dẫn đến path operation)
            scheme_name (Optional[str]): Tên của scheme bảo mật trong OpenAPI
            scopes (Optional[Dict[str, str]]): Các scopes OAuth2 được yêu cầu
            description (Optional[str]): Mô tả scheme bảo mật trong OpenAPI
            auto_error (bool): Tự động báo lỗi khi không tìm thấy token
            cookie_name (Optional[str]): Tên của cookie chứa token, mặc định lấy từ settings
        """
        if not scopes:
            scopes = {}

        # Sử dụng tên cookie từ tham số hoặc settings nếu không được cung cấp
        self.cookie_name = cookie_name or settings.COOKIE_NAME

        flows = OAuthFlowsModel(
            password=cast(Any, {"tokenUrl": tokenUrl, "scopes": scopes})
        )

        super().__init__(
            flows=flows,
            scheme_name=scheme_name,
            description=description,
            auto_error=auto_error,
        )

    async def __call__(self, request: Request) -> Optional[str]:
        # Lấy token từ cookie
        token = request.cookies.get(self.cookie_name)

        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            else:
                return None

        return token
