# -*- coding: utf-8 -*-
"""
单点登录：接收主系统 OA 的 ticket，校验后按用户名映射建立登录态并重定向到前端。
与主系统约定：ticket 格式与校验方式见 OA 系统文档；本系统按 ticket 中的 name 匹配 User.username 或 User.real_name。
"""
import base64
import hmac
import hashlib
import json
import logging
import time
from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.auth.security import create_access_token
from app.config import settings
from app.database import get_session
from app.models import User

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sso", tags=["sso"])


def _verify_ticket(ticket: str) -> dict | None:
    """校验 OA 下发的 ticket，返回解析后的 payload 或 None。"""
    secret = (getattr(settings, "sso_secret", None) or "").strip()
    if not secret or "." not in ticket:
        return None
    payload_b64, sig = ticket.split(".", 1)
    payload_b64_padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
    computed = hmac.new(
        secret.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    if computed != sig:
        return None
    try:
        raw = base64.urlsafe_b64decode(payload_b64_padded)
        data = json.loads(raw)
    except Exception:
        return None
    if data.get("exp", 0) < time.time():
        return None
    return data


@router.get("/entry")
def sso_entry(
    ticket: str = Query(..., description="主系统下发的 SSO ticket"),
    session: Session = Depends(get_session),
):
    """
    接收主系统 OA 的 ticket，校验签名与有效期后，按 name（用户名/姓名）匹配本系统用户，
    生成 JWT 并重定向到前端，前端通过 sso_token 参数写入 localStorage 完成登录。
    """
    if not ticket or not ticket.strip():
        return RedirectResponse(url=_login_url_with_error("missing_ticket"), status_code=302)

    secret = (getattr(settings, "sso_secret", None) or "").strip()
    if not secret:
        return RedirectResponse(url=_login_url_with_error("sso_not_configured"), status_code=302)

    payload = _verify_ticket(ticket.strip())
    if not payload:
        logger.warning("SSO ticket 校验失败（签名/过期或格式错误）")
        return RedirectResponse(url=_login_url_with_error("invalid_ticket"), status_code=302)

    name = (payload.get("name") or payload.get("sub") or "").strip()
    if not name:
        logger.warning("SSO ticket 中无 name/sub")
        return RedirectResponse(url=_login_url_with_error("invalid_ticket"), status_code=302)

    # 用户名映射：先按 username，再按 real_name
    user = session.exec(
        select(User).where(
            (User.username == name) | (User.real_name == name)
        ).limit(1)
    ).first()
    if not user:
        logger.warning("SSO 用户名未找到: name=%r（需与本系统 User.username 或 User.real_name 一致）", name)
        return RedirectResponse(url=_login_url_with_error("user_not_found"), status_code=302)

    expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=expires,
    )

    base_url = (getattr(settings, "frontend_base_url", None) or "").strip().rstrip("/")
    if not base_url:
        logger.error("SSO 成功但未配置 frontend_base_url，无法重定向到前端")
        return RedirectResponse(url=_login_url_with_error("sso_not_configured"), status_code=302)
    redirect_url = f"{base_url}/?sso_token={access_token}"
    logger.info("SSO 登录成功: user=%s, 重定向至前端", user.username)
    return RedirectResponse(url=redirect_url, status_code=302)


def _login_url_with_error(error: str) -> str:
    """前端登录页 URL（带错误码），用于 SSO 校验失败时重定向。"""
    base = (getattr(settings, "frontend_base_url", None) or "").strip().rstrip("/")
    if base:
        return f"{base}/login?error={error}"
    return f"/login?error={error}"
