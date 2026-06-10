"""FastAPI + Jinja2 + HTMX HTML surfaces (no Node.js)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, Form, HTTPException, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from api.journey_dispatch import dispatch_action
from api.persistence import COOKIE_NAME, cookie_settings, is_resumable, load_context
from api.sessions import clear_session, create_session, get_engine, get_session, save_session
from api.view_helpers import build_view_context
from engine.customer_copy import is_fbo_payable_line
from engine.models import JourneyScreen

TEMPLATES_DIR = Path(__file__).resolve().parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["html"])

templates.env.globals["is_fbo_payable_line"] = is_fbo_payable_line


def _set_session_cookie(response: Response, journey_id: str) -> None:
    response.set_cookie(value=journey_id, **cookie_settings())


def _clear_session_cookie(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, httponly=True, samesite="lax")


def _resolve_session(
    request: Request,
    *,
    fresh: bool = False,
) -> tuple[str, bool]:
    """Return (journey_id, welcome_back). Creates a session when needed."""
    cookie_id = request.cookies.get(COOKIE_NAME)
    if not fresh and cookie_id:
        ctx = load_context(cookie_id)
        if ctx is not None and is_resumable(ctx):
            get_session(cookie_id)
            return cookie_id, True

    ctx = create_session()
    return ctx.journey_id, False


def _render_workspace(
    request: Request,
    *,
    mode: str,
    journey_id: str,
    welcome_back: bool = False,
    show_provider_picker: bool = False,
    error: str | None = None,
    read_only: bool = False,
    embed_theme: str = "default",
    include_intel: bool = False,
    template_name: str = "surfaces/customer.html",
) -> HTMLResponse:
    ctx = get_session(journey_id)
    screen = get_engine().render(ctx)
    view = build_view_context(
        ctx,
        screen,
        mode=mode,  # type: ignore[arg-type]
        include_intel=include_intel,
        welcome_back=welcome_back,
        show_provider_picker=show_provider_picker,
        error=error,
        read_only=read_only,
        embed_theme=embed_theme,
    )
    response = templates.TemplateResponse(
        request,
        template_name,
        view,
    )
    _set_session_cookie(response, journey_id)
    return response


def _render_step_partial(
    request: Request,
    journey_id: str,
    *,
    mode: str = "customer",
    welcome_back: bool = False,
    show_provider_picker: bool = False,
    error: str | None = None,
    read_only: bool = False,
    embed_theme: str = "default",
    include_intel: bool = False,
    oob_targets: list[str] | None = None,
) -> HTMLResponse:
    ctx = get_session(journey_id)
    screen = get_engine().render(ctx)
    view = build_view_context(
        ctx,
        screen,
        mode=mode,  # type: ignore[arg-type]
        include_intel=include_intel,
        welcome_back=welcome_back,
        show_provider_picker=show_provider_picker,
        error=error,
        read_only=read_only,
        embed_theme=embed_theme,
    )
    view["oob_targets"] = oob_targets or []
    if oob_targets:
        view["agent_oob"] = build_view_context(
            ctx,
            screen,
            mode="agent",
            include_intel=True,
            read_only=True,
        )
        view["embed_oob"] = build_view_context(
            ctx,
            screen,
            mode="embed",
            read_only=True,
            embed_theme="minimal",
        )
    response = templates.TemplateResponse(
        request,
        "partials/journey_swap.html",
        view,
    )
    _set_session_cookie(response, journey_id)
    return response


def _apply_form_action(journey_id: str, form: dict[str, Any]) -> JourneyScreen | dict[str, Any]:
    ctx = get_session(journey_id)
    return dispatch_action(ctx, form)


@router.get("/", response_class=HTMLResponse)
def root():
    return RedirectResponse("/customer", status_code=302)


@router.get("/customer", response_class=HTMLResponse)
def customer_page(request: Request, fresh: bool = False):
    journey_id, welcome_back = _resolve_session(request, fresh=fresh)
    return _render_workspace(
        request,
        mode="customer",
        journey_id=journey_id,
        welcome_back=welcome_back and not fresh,
        template_name="surfaces/customer.html",
    )


@router.get("/agent", response_class=HTMLResponse)
def agent_page(request: Request, fresh: bool = False):
    journey_id, welcome_back = _resolve_session(request, fresh=fresh)
    return _render_workspace(
        request,
        mode="agent",
        journey_id=journey_id,
        welcome_back=welcome_back and not fresh,
        include_intel=True,
        template_name="surfaces/agent.html",
    )


@router.get("/embed", response_class=HTMLResponse)
def embed_page(request: Request, fresh: bool = False, theme: str = "default"):
    journey_id, welcome_back = _resolve_session(request, fresh=fresh)
    return _render_workspace(
        request,
        mode="embed",
        journey_id=journey_id,
        welcome_back=welcome_back and not fresh,
        read_only=True,
        embed_theme=theme,
        template_name="surfaces/embed.html",
    )


@router.get("/sandbox", response_class=HTMLResponse)
def sandbox_page(request: Request, fresh: bool = False):
    journey_id, welcome_back = _resolve_session(request, fresh=fresh)
    ctx = get_session(journey_id)
    screen = get_engine().render(ctx)
    customer_view = build_view_context(
        ctx,
        screen,
        mode="customer",
        welcome_back=welcome_back and not fresh,
    )
    agent_view = build_view_context(
        ctx,
        screen,
        mode="agent",
        include_intel=True,
        welcome_back=False,
        read_only=True,
    )
    embed_view = build_view_context(
        ctx,
        screen,
        mode="embed",
        read_only=True,
        embed_theme="minimal",
    )
    response = templates.TemplateResponse(
        request,
        "surfaces/sandbox.html",
        {
            "customer": customer_view,
            "agent": agent_view,
            "embed": embed_view,
            "journey_id": journey_id,
        },
    )
    _set_session_cookie(response, journey_id)
    return response


@router.post("/htmx/journey/action", response_class=HTMLResponse)
async def htmx_journey_action(
    request: Request,
    journey_id: str = Form(...),
    action_type: str = Form(..., alias="type"),
    employer: str | None = Form(None),
    provider: str | None = Form(None),
    answer: str | None = Form(None),
    can_login: str | None = Form(None),
    tax_type: str | None = Form(None),
    channel: str | None = Form(None),
    outcome: str | None = Form(None),
    reason: str | None = Form(None),
    surface: str = Form("customer"),
    show_provider_picker: str | None = Form(None),
    embed_theme: str = Form("default"),
):
    body: dict[str, Any] = {"type": action_type}
    if employer:
        body["employer"] = employer.strip()
    if provider:
        body["provider"] = provider.strip()
    if answer:
        body["answer"] = answer.strip()
    if can_login is not None and can_login != "":
        body["can_login"] = can_login.lower() in {"1", "true", "yes", "on"}
    if tax_type:
        body["tax_type"] = tax_type
    if channel:
        body["channel"] = channel
    if outcome:
        body["outcome"] = outcome
    if reason:
        body["reason"] = reason

    picker = show_provider_picker in {"1", "true", "on"}
    read_only = surface in {"agent", "embed"}
    include_intel = surface == "agent"

    try:
        result = _apply_form_action(journey_id, body)
    except HTTPException as exc:
        return _render_step_partial(
            request,
            journey_id,
            mode=surface,
            error=str(exc.detail),
            show_provider_picker=picker,
            read_only=read_only,
            embed_theme=embed_theme,
            include_intel=include_intel,
            oob_targets=["sandbox-agent", "sandbox-embed"] if surface == "customer" else [],
        )

    if isinstance(result, dict):
        screen = result["screen"]
        save_session(get_session(journey_id))
    else:
        screen = result

    oob: list[str] = []
    if surface == "customer":
        oob = ["sandbox-agent", "sandbox-embed"]

    return _render_step_partial(
        request,
        journey_id,
        mode=surface,
        show_provider_picker=picker,
        read_only=read_only,
        embed_theme=embed_theme,
        include_intel=include_intel,
        oob_targets=oob,
    )


@router.post("/htmx/journey/restart", response_class=HTMLResponse)
async def htmx_restart(
    request: Request,
    journey_id: str = Form(...),
    surface: str = Form("customer"),
):
    clear_session(journey_id)
    ctx = create_session()
    response = _render_step_partial(
        request,
        ctx.journey_id,
        mode=surface,
        welcome_back=False,
    )
    _clear_session_cookie(response)
    _set_session_cookie(response, ctx.journey_id)
    return response


@router.post("/htmx/journey/toggle-picker", response_class=HTMLResponse)
async def htmx_toggle_picker(
    request: Request,
    journey_id: str = Form(...),
    show_provider_picker: str = Form("false"),
    surface: str = Form("customer"),
):
    picker = show_provider_picker.lower() in {"1", "true", "on"}
    return _render_step_partial(
        request,
        journey_id,
        mode=surface,
        show_provider_picker=picker,
    )
