# -*- coding: utf-8 -*-
"""
单点登录：接收主系统 OA 的 ticket，校验后按用户名映射建立登录态并重定向到前端。
"""
import base64
import hmac
import hashlib
import json
import time
from datetime import timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from app.auth.security import create_access_token
from app.config import settings
from app.database import get_session
from app.models import User

router = APIRouter(prefix="/sso", tags=["sso"])


def _verify_ticket(ticket: str) -> dict | None:
    """校验 OA 下发的 ticket，返回解析后的 payload 或 None。"""
    secret = (getattr(settings, "sso_secret", None) or "").strip()
    if not secret or "." not in ticket:
        print(f"[SSO] 校验前置失败: secret为空={not secret}, ticket无点号={'.' not in ticket}")
        return None
    payload_b64, sig = ticket.split(".", 1)
    payload_b64_padded = payload_b64 + "=" * (4 - len(payload_b64) % 4)
    computed = hmac.new(
        secret.encode("utf-8"),
        payload_b64.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    print(f"[SSO] 签名校验: computed={computed[:16]}..., received={sig[:16]}..., match={computed == sig}")
    if computed != sig:
        return None
    try:
        raw = base64.urlsafe_b64decode(payload_b64_padded)
        data = json.loads(raw)
        print(f"[SSO] payload 解析成功: {data}")
    except Exception as e:
        print(f"[SSO] payload 解析失败: {e}")
        return None
    now = time.time()
    if data.get("exp", 0) < now:
        print(f"[SSO] ticket 已过期: exp={data.get('exp')}, now={now}")
        return None
    return data


def _login_url_with_error(error: str) -> str:
    base = (getattr(settings, "frontend_base_url", None) or "").strip().rstrip("/")
    if base:
        return f"{base}/login?error={error}"
    return f"/login?error={error}"


@router.get("/entry")
def sso_entry(
    ticket: str = Query(..., description="主系统下发的 SSO ticket"),
    session: Session = Depends(get_session),
):
    print(f"\n{'='*60}")
    print(f"[SSO] 收到 SSO 请求, ticket 前30字符: {ticket[:30]}...")
    print(f"[SSO] sso_secret: '{settings.sso_secret[:4]}...' (长度{len(settings.sso_secret)})")
    print(f"[SSO] frontend_base_url: '{settings.frontend_base_url}'")

    if not ticket or not ticket.strip():
        url = _login_url_with_error("missing_ticket")
        print(f"[SSO] 失败: ticket 为空, 重定向到 {url}")
        return RedirectResponse(url=url, status_code=302)

    secret = (getattr(settings, "sso_secret", None) or "").strip()
    if not secret:
        url = _login_url_with_error("sso_not_configured")
        print(f"[SSO] 失败: sso_secret 未配置, 重定向到 {url}")
        return RedirectResponse(url=url, status_code=302)

    payload = _verify_ticket(ticket.strip())
    if not payload:
        url = _login_url_with_error("invalid_ticket")
        print(f"[SSO] 失败: ticket 校验不通过, 重定向到 {url}")
        return RedirectResponse(url=url, status_code=302)

    name = (payload.get("name") or payload.get("sub") or "").strip()
    if not name:
        url = _login_url_with_error("invalid_ticket")
        print(f"[SSO] 失败: ticket 中无 name/sub, 重定向到 {url}")
        return RedirectResponse(url=url, status_code=302)

    print(f"[SSO] 从 ticket 提取到 name: '{name}'")

    # 用户名映射：先按 username，再按 real_name
    user = session.exec(
        select(User).where(
            (User.username == name) | (User.real_name == name)
        ).limit(1)
    ).first()

    if not user:
        # 额外调试：列出数据库中所有用户以对比
        all_users = session.exec(select(User)).all()
        print(f"[SSO] 失败: 未找到用户 name='{name}'")
        print(f"[SSO] 数据库中共 {len(all_users)} 个用户:")
        for u in all_users[:20]:
            print(f"  - id={u.id}, username='{u.username}', real_name='{u.real_name}', role={u.role}")
        url = _login_url_with_error("user_not_found")
        print(f"[SSO] 重定向到 {url}")
        return RedirectResponse(url=url, status_code=302)

    print(f"[SSO] 匹配到用户: id={user.id}, username='{user.username}', real_name='{user.real_name}', role={user.role}")

    expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role.value},
        expires_delta=expires,
    )

    base_url = (getattr(settings, "frontend_base_url", None) or "").strip().rstrip("/")
    if not base_url:
        url = _login_url_with_error("sso_not_configured")
        print(f"[SSO] 失败: frontend_base_url 为空, 重定向到 {url}")
        return RedirectResponse(url=url, status_code=302)

    redirect_url = f"{base_url}/?sso_token={access_token}"
    print(f"[SSO] 成功! 重定向到: {redirect_url[:80]}...")
    print(f"{'='*60}\n")
    return RedirectResponse(url=redirect_url, status_code=302)
