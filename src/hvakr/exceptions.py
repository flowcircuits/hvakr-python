"""HVAKR API exceptions."""

from typing import Any


class HVAKRClientError(Exception):
    """Error thrown when the HVAKR API returns an unsuccessful response.

    Attributes:
        message: The error message.
        status_code: The HTTP status code from the response.
        metadata: Additional error details from the API response.
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        metadata: Any = None,
    ) -> None:
        """Initialize the error.

        Args:
            message: The error message.
            status_code: The HTTP status code from the response.
            metadata: Additional error details from the API response.
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.metadata = metadata

    def __str__(self) -> str:
        if self.status_code:
            return f"Error {self.status_code}: {self.message}"
        return self.message

    def __repr__(self) -> str:
        return (
            f"HVAKRClientError(message={self.message!r}, "
            f"status_code={self.status_code!r}, metadata={self.metadata!r})"
        )
