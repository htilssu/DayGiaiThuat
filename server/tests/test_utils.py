"""
Tests cho các utility functions trong ứng dụng.
"""

from datetime import datetime, timedelta
from jose import jwt

from app.utils.utils import (
    verify_password,
    password_hash,
    create_access_token,
    ALGORITHM,
)
from app.utils.case_utils import (
    to_camel_case,
    to_snake_case,
    convert_dict_to_camel_case,
    convert_dict_to_snake_case,
)
from app.core.config import settings


class TestAuthUtils:
    """Tests cho các utility functions liên quan đến xác thực."""

    def test_password_hash(self):
        """Test hash và verify password."""
        password = "password123"
        hashed_password = password_hash(password)

        # Kiểm tra hashed_password khác với password gốc
        assert hashed_password != password

        # Kiểm tra verify_password hoạt động đúng
        assert verify_password(password, hashed_password) is True
        assert verify_password("wrong_password", hashed_password) is False

    def test_create_access_token(self):
        """Test tạo JWT token."""
        data = {"sub": "test@example.com"}
        token = create_access_token(data)

        # Giải mã token để kiểm tra
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        # Kiểm tra dữ liệu trong token
        assert payload["sub"] == data["sub"]
        assert "exp" in payload
        assert "iat" in payload

        # Kiểm tra thời gian hết hạn
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        assert (
            exp_time - iat_time
        ).total_seconds() == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60

    def test_create_access_token_with_custom_expiry(self):
        """Test tạo JWT token với thời gian hết hạn tùy chỉnh."""
        data = {"sub": "test@example.com"}
        expires_delta = timedelta(minutes=30)
        token = create_access_token(data, expires_delta=expires_delta)

        # Giải mã token để kiểm tra
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])

        # Kiểm tra thời gian hết hạn
        exp_time = datetime.fromtimestamp(payload["exp"])
        iat_time = datetime.fromtimestamp(payload["iat"])
        assert (exp_time - iat_time).total_seconds() == expires_delta.total_seconds()


class TestCaseUtils:
    """Tests cho các utility functions liên quan đến chuyển đổi case."""

    def test_to_camel_case(self):
        """Test chuyển đổi từ snake_case sang camelCase."""
        assert to_camel_case("hello_world") == "helloWorld"
        assert to_camel_case("user_profile_data") == "userProfileData"
        assert to_camel_case("api_key") == "apiKey"
        assert to_camel_case("") == ""
        assert to_camel_case("already_camel") == "alreadyCamel"
        assert to_camel_case("single") == "single"

    def test_to_snake_case(self):
        """Test chuyển đổi từ camelCase sang snake_case."""
        assert to_snake_case("helloWorld") == "hello_world"
        assert to_snake_case("userProfileData") == "user_profile_data"
        assert to_snake_case("apiKey") == "api_key"
        assert to_snake_case("") == ""
        assert to_snake_case("already_snake") == "already_snake"
        assert to_snake_case("single") == "single"

    def test_convert_dict_to_camel_case(self):
        """Test chuyển đổi dictionary từ snake_case sang camelCase."""
        # Test với dictionary đơn giản
        snake_dict = {
            "user_name": "test",
            "email_address": "test@example.com",
            "is_active": True,
        }
        expected_camel_dict = {
            "userName": "test",
            "emailAddress": "test@example.com",
            "isActive": True,
        }
        assert convert_dict_to_camel_case(snake_dict) == expected_camel_dict

        # Test với dictionary lồng nhau
        nested_snake_dict = {
            "user_data": {
                "first_name": "John",
                "last_name": "Doe",
                "contact_info": {
                    "email_address": "john@example.com",
                    "phone_number": "123456789",
                },
            },
            "is_verified": True,
            "access_levels": ["admin", "user"],
        }
        expected_nested_camel_dict = {
            "userData": {
                "firstName": "John",
                "lastName": "Doe",
                "contactInfo": {
                    "emailAddress": "john@example.com",
                    "phoneNumber": "123456789",
                },
            },
            "isVerified": True,
            "accessLevels": ["admin", "user"],
        }
        assert (
            convert_dict_to_camel_case(nested_snake_dict) == expected_nested_camel_dict
        )

    def test_convert_dict_to_snake_case(self):
        """Test chuyển đổi dictionary từ camelCase sang snake_case."""
        # Test với dictionary đơn giản
        camel_dict = {
            "userName": "test",
            "emailAddress": "test@example.com",
            "isActive": True,
        }
        expected_snake_dict = {
            "user_name": "test",
            "email_address": "test@example.com",
            "is_active": True,
        }
        assert convert_dict_to_snake_case(camel_dict) == expected_snake_dict

        # Test với dictionary lồng nhau
        nested_camel_dict = {
            "userData": {
                "firstName": "John",
                "lastName": "Doe",
                "contactInfo": {
                    "emailAddress": "john@example.com",
                    "phoneNumber": "123456789",
                },
            },
            "isVerified": True,
            "accessLevels": ["admin", "user"],
        }
        expected_nested_snake_dict = {
            "user_data": {
                "first_name": "John",
                "last_name": "Doe",
                "contact_info": {
                    "email_address": "john@example.com",
                    "phone_number": "123456789",
                },
            },
            "is_verified": True,
            "access_levels": ["admin", "user"],
        }
        assert (
            convert_dict_to_snake_case(nested_camel_dict) == expected_nested_snake_dict
        )
