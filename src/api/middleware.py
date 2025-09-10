"""
API Middleware for Error Handling

This module provides middleware for handling domain errors in API responses.
"""

import logging
from typing import Callable
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

from domain.errors import (
    DomainError, ValidationError, ResourceNotFoundError,
    ExternalServiceError, ConfigurationError, handle_domain_error
)

logger = logging.getLogger(__name__)


async def error_handling_middleware(request: Request, call_next: Callable):
    """
    Middleware for handling domain errors and converting them to appropriate HTTP responses

    Args:
        request: FastAPI request object
        call_next: Next middleware/callable in chain

    Returns:
        HTTP response with appropriate error format
    """
    try:
        response = await call_next(request)
        return response

    except DomainError as e:
        # Handle domain-specific errors
        error_response = handle_domain_error(e)
        logger.warning(f"Domain error handled: {e.message}", extra={
            "error_type": e.__class__.__name__,
            "details": e.details,
            "path": request.url.path,
            "method": request.method
        })

        return JSONResponse(
            status_code=error_response["status_code"],
            content=error_response["error"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise

    except Exception as e:
        # Handle unexpected errors
        logger.error(f"Unexpected error: {str(e)}", exc_info=True, extra={
            "path": request.url.path,
            "method": request.method,
            "user_agent": request.headers.get("user-agent", "unknown")
        })

        return JSONResponse(
            status_code=500,
            content={
                "error": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": "2024-01-01T00:00:00Z"  # Would be actual timestamp
            }
        )


def create_request_id_middleware():
    """
    Middleware for adding request IDs to requests

    Returns:
        Middleware function
    """
    import uuid

    async def request_id_middleware(request: Request, call_next: Callable):
        # Add request ID to request state
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Add request ID to response headers
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response

    return request_id_middleware


def create_logging_middleware():
    """
    Middleware for logging API requests and responses

    Returns:
        Middleware function
    """

    async def logging_middleware(request: Request, call_next: Callable):
        import time

        start_time = time.time()

        logger.info(f"Request started: {request.method} {request.url.path}", extra={
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "user_agent": request.headers.get("user-agent", "unknown"),
            "request_id": getattr(request.state, "request_id", None)
        })

        try:
            response = await call_next(request)

            duration = time.time() - start_time
            logger.info(f"Request completed: {request.method} {request.url.path} - {response.status_code}", extra={
                "status_code": response.status_code,
                "duration": duration,
                "request_id": getattr(request.state, "request_id", None)
            })

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url.path}", extra={
                "error": str(e),
                "duration": duration,
                "request_id": getattr(request.state, "request_id", None)
            })
            raise


class ErrorHandler:
    """
    Utility class for handling and formatting errors consistently
    """

    @staticmethod
    def handle_cli_error(error: Exception) -> str:
        """
        Handle errors in CLI context

        Args:
            error: The exception that occurred

        Returns:
            Formatted error message for CLI display
        """
        if isinstance(error, DomainError):
            error_info = error.to_dict()
            message = f"[red]Error: {error_info['message']}[/red]"

            if error_info.get('details'):
                details = "\n".join(f"  {k}: {v}" for k, v in error_info['details'].items())
                message += f"\n[yellow]Details:[/yellow]\n{details}"

            return message

        elif isinstance(error, Exception):
            return f"[red]Unexpected error: {str(error)}[/red]"

        return "[red]An unknown error occurred[/red]"

    @staticmethod
    def log_error(error: Exception, context: str = "", extra_data: dict = None):
        """
        Log an error with appropriate context

        Args:
            error: The exception that occurred
            context: Additional context information
            extra_data: Extra data to include in log
        """
        extra = extra_data or {}

        if context:
            extra["context"] = context

        if isinstance(error, DomainError):
            logger.warning(f"Domain error: {error.message}", extra={
                **extra,
                "error_type": error.__class__.__name__,
                "details": error.details
            })
        else:
            logger.error(f"Unexpected error: {str(error)}", exc_info=True, extra=extra)
