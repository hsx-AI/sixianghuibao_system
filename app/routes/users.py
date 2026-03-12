from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlmodel import Session, select

from app.auth.dependencies import get_current_user, require_roles
from app.database import get_session
from app.models.user import Role, User

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCreate(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=2, max_length=50)
    password: str = Field(..., min_length=4, max_length=50)
    real_name: str = Field(..., min_length=1, max_length=50)
    role: str = Field(...)
    zhibu: Optional[str] = Field(None, max_length=50)
    pyr1: Optional[str] = Field(None, max_length=50)
    pyr2: Optional[str] = Field(None, max_length=50)


class UserUpdate(BaseModel):
    """更新用户请求"""
    username: Optional[str] = Field(None, min_length=2, max_length=50)
    password: Optional[str] = Field(None, min_length=4, max_length=50)
    real_name: Optional[str] = Field(None, min_length=1, max_length=50)
    role: Optional[str] = Field(None)
    zhibu: Optional[str] = Field(None, max_length=50)
    pyr1: Optional[str] = Field(None, max_length=50)
    pyr2: Optional[str] = Field(None, max_length=50)


@router.get("/list")
def list_all_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> List[Dict]:
    """
    获取所有用户列表（管理员专用）
    """
    users = session.exec(select(User).order_by(User.id)).all()
    
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "username": user.username,
            "real_name": user.real_name,
            "role": user.role,
            "zhibu": user.zhibu,
            "pyr1": user.pyr1,
            "pyr2": user.pyr2,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return result


@router.post("")
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    创建新用户（管理员专用）
    """
    # 检查用户名是否已存在
    existing = session.exec(select(User).where(User.username == payload.username)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已存在"
        )
    
    # 验证角色
    try:
        role = Role(payload.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"无效的角色: {payload.role}"
        )
    
    # 创建用户
    user = User(
        username=payload.username,
        password_hash=pwd_context.hash(payload.password),
        real_name=payload.real_name,
        role=role,
        zhibu=payload.zhibu,
        pyr1=payload.pyr1,
        pyr2=payload.pyr2
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "role": user.role,
        "zhibu": user.zhibu,
        "message": "用户创建成功"
    }


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    更新用户信息（管理员专用）
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 检查用户名是否重复
    if payload.username and payload.username != user.username:
        existing = session.exec(select(User).where(User.username == payload.username)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        user.username = payload.username
    
    # 更新密码
    if payload.password:
        user.password_hash = pwd_context.hash(payload.password)
    
    # 更新其他字段
    if payload.real_name is not None:
        user.real_name = payload.real_name
    
    if payload.role is not None:
        try:
            user.role = Role(payload.role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"无效的角色: {payload.role}"
            )
    
    if payload.zhibu is not None:
        user.zhibu = payload.zhibu if payload.zhibu else None
    
    if payload.pyr1 is not None:
        user.pyr1 = payload.pyr1 if payload.pyr1 else None
    
    if payload.pyr2 is not None:
        user.pyr2 = payload.pyr2 if payload.pyr2 else None
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "real_name": user.real_name,
        "role": user.role,
        "zhibu": user.zhibu,
        "pyr1": user.pyr1,
        "pyr2": user.pyr2,
        "message": "用户更新成功"
    }


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ADMIN)),
) -> Dict:
    """
    删除用户（管理员专用）
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    # 不能删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )
    
    session.delete(user)
    session.commit()
    
    return {"message": "用户删除成功"}


@router.get("/organization/zhibu")
def get_zhibu_organization(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ZZWY, Role.ZBSJ)),
) -> Dict:
    """
    获取当前用户所属支部的组织架构数据（组织委员和支部书记专用）
    
    返回当前支部的人员信息，包含：
    - 支部名称
    - 各角色人员列表（支部书记、组织委员、培养人、积极分子）
    - 积极分子的培养人关系
    """
    if not current_user.zhibu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前用户未设置所属支部"
        )
    
    # 查询当前支部的所有用户
    users = session.exec(
        select(User).where(User.zhibu == current_user.zhibu)
    ).all()
    
    zhibu_data = {
        "name": current_user.zhibu,
        "zbsj": [],
        "zzwy": [],
        "pyr": [],
        "activist": [],
    }
    
    for user in users:
        user_info = {
            "id": user.id,
            "real_name": user.real_name,
            "role": user.role,
            "username": user.username,
        }
        
        if user.role == Role.ZBSJ:
            zhibu_data["zbsj"].append(user_info)
        elif user.role == Role.ZZWY:
            zhibu_data["zzwy"].append(user_info)
        elif user.role == Role.PYR:
            zhibu_data["pyr"].append(user_info)
        elif user.role == Role.ACTIVIST:
            user_info["pyr1"] = user.pyr1
            user_info["pyr2"] = user.pyr2
            zhibu_data["activist"].append(user_info)
    
    return zhibu_data


@router.get("/organization")
def get_organization_structure(
    session: Session = Depends(get_session),
    current_user: User = Depends(require_roles(Role.ZZS)),
) -> Dict:
    """
    获取组织架构数据（仅供总支书查看）
    
    返回按支部分组的人员信息，包含：
    - 支部名称
    - 各角色人员列表（支部书记、组织委员、培养人、积极分子）
    - 积极分子的培养人关系
    """
    # 查询所有用户
    users = session.exec(select(User)).all()
    
    # 按支部分组
    zhibu_map: Dict[str, Dict] = {}
    
    # 总支书记单独列出
    zzs_list = []
    
    for user in users:
        user_info = {
            "id": user.id,
            "real_name": user.real_name,
            "role": user.role,
            "username": user.username,
        }
        
        # 总支书记不属于任何支部
        if user.role == Role.ZZS:
            zzs_list.append(user_info)
            continue
        
        # 管理员跳过
        if user.role == Role.ADMIN:
            continue
        
        zhibu = user.zhibu or "未分配支部"
        
        if zhibu not in zhibu_map:
            zhibu_map[zhibu] = {
                "name": zhibu,
                "zbsj": [],      # 支部书记
                "zzwy": [],      # 组织委员
                "pyr": [],       # 培养人
                "activist": [],  # 积极分子
            }
        
        if user.role == Role.ZBSJ:
            zhibu_map[zhibu]["zbsj"].append(user_info)
        elif user.role == Role.ZZWY:
            zhibu_map[zhibu]["zzwy"].append(user_info)
        elif user.role == Role.PYR:
            zhibu_map[zhibu]["pyr"].append(user_info)
        elif user.role == Role.ACTIVIST:
            # 积极分子额外包含培养人信息
            user_info["pyr1"] = user.pyr1
            user_info["pyr2"] = user.pyr2
            zhibu_map[zhibu]["activist"].append(user_info)
    
    # 转换为列表并排序
    zhibu_list = sorted(zhibu_map.values(), key=lambda x: x["name"])
    
    return {
        "zzs": zzs_list,
        "zhibu_list": zhibu_list
    }

