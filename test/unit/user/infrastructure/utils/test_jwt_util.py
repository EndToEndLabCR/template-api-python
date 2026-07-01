"""Unit tests for jwt_util — JWT creation and decoding."""

import pytest


class TestCreateAccessToken:
    """Tests for create_access_token."""

    @pytest.mark.unit
    def test_create_access_token_returns_string(self) -> None:
        """Should return a non-empty string token."""
        from src.shared.utils.jwt_util import create_access_token

        token = create_access_token({"sub": "user-id"})
        assert isinstance(token, str)
        assert len(token) > 0

    @pytest.mark.unit
    def test_create_access_token_contains_data(self) -> None:
        """Token payload should contain the data passed in."""
        from src.shared.utils.jwt_util import create_access_token, decode_access_token

        payload = {"sub": "user-id", "role": "admin"}
        token = create_access_token(payload)
        decoded = decode_access_token(token)

        assert decoded["sub"] == "user-id"
        assert decoded["role"] == "admin"

    @pytest.mark.unit
    def test_token_contains_exp_claim(self) -> None:
        """Token should include an 'exp' claim (expiration timestamp)."""
        from src.shared.utils.jwt_util import create_access_token, decode_access_token

        token = create_access_token({"sub": "user-id"})
        decoded = decode_access_token(token)

        assert "exp" in decoded
        assert isinstance(decoded["exp"], int)

    @pytest.mark.unit
    def test_create_access_token_encodes_and_decodes(self) -> None:
        """create_access_token should produce a token that decode_access_token can decode."""
        from src.shared.utils.jwt_util import create_access_token, decode_access_token

        token = create_access_token({"sub": "user-id"})
        decoded = decode_access_token(token)
        assert decoded["sub"] == "user-id"

    @pytest.mark.unit
    def test_custom_expires_delta(self) -> None:
        """Custom expires_delta should be respected (token valid ~1 second)."""
        from datetime import timedelta
        from src.shared.utils.jwt_util import create_access_token, decode_access_token

        token = create_access_token({"sub": "short-lived"}, expires_delta=timedelta(seconds=1))
        decoded = decode_access_token(token)
        assert decoded["sub"] == "short-lived"


class TestDecodeAccessToken:
    """Tests for decode_access_token."""

    @pytest.mark.unit
    def test_decode_access_token_raises_error_for_invalid_token(self) -> None:
        """Decoding a garbage token should raise jwt.PyJWTError."""
        import jwt
        from src.shared.utils.jwt_util import decode_access_token

        with pytest.raises(jwt.PyJWTError):
            decode_access_token("this.is.not.a.valid.jwt")

    @pytest.mark.unit
    def test_decode_access_token_raises_error_for_empty_token(self) -> None:
        """Decoding an empty token should raise jwt.PyJWTError."""
        import jwt
        from src.shared.utils.jwt_util import decode_access_token

        with pytest.raises(jwt.PyJWTError):
            decode_access_token("")

    @pytest.mark.unit
    def test_decode_access_token_raises_expired_error(self) -> None:
        """An expired token should raise jwt.ExpiredSignatureError."""
        from datetime import timedelta, datetime, timezone
        import jwt
        from src.shared.utils.jwt_util import create_access_token, decode_access_token

        # Create a token that expired 1 second ago
        token = create_access_token(
            {"sub": "expired-user"},
            expires_delta=timedelta(seconds=-10),
        )
        # Manually set exp in the past to guarantee expiry
        import src.shared.utils.jwt_util as jwt_util

        past_exp = int(datetime.now(timezone.utc).timestamp()) - 60
        payload = {"sub": "expired-user", "exp": past_exp}
        expired_token = jwt.encode(payload, jwt_util.SECRET_KEY, algorithm=jwt_util.ALGORITHM)

        with pytest.raises(jwt.ExpiredSignatureError):
            decode_access_token(expired_token)

    @pytest.mark.unit
    def test_decode_access_token_raises_error_for_token_signed_with_different_key(
        self,
    ) -> None:
        """Token signed with a different key should raise jwt.PyJWTError."""
        import jwt
        from src.shared.utils.jwt_util import decode_access_token

        payload = {"sub": "user-id", "exp": 9999999999}
        wrong_key_token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")

        with pytest.raises(jwt.PyJWTError):
            decode_access_token(wrong_key_token)
