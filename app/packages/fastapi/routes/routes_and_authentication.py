"""The FastAPI routes"""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles
from werkzeug.security import generate_password_hash
import jwt

from app.packages import handle_passwords, log_events
from app.packages.database.models import models
from app.packages.fastapi.models.fastapi_models import (
    NewUserInDBModel,
    Token,
)
from .dependencies import (
    get_current_active_user,
    session,
    authenticate_user,
    SECRET_KEY,
    ALGORITHM,
)


# Because of the current architecture, in order to run tests_users and tests_authentication
# We set "noqa: F401" for the unused get_user dependencie.
from .dependencies import get_user  # noqa: F401
from .routers import books_categories, books, comments, quotes, users


ACCESS_TOKEN_EXPIRE_MINUTES = 30
app: FastAPI = FastAPI(
    title="DUMMY-OPS API",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)
app.mount("/api/v1/static", StaticFiles(directory="app/packages/fastapi/static"), name="static")
templates = Jinja2Templates(directory="app/packages/fastapi/routes/templates")


protected_routes = [
    books_categories.router,
    books.router,
    comments.router,
    quotes.router,
    users.router,
]

for router in protected_routes:
    app.include_router(router, dependencies=[Depends(get_current_active_user)])


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """create an access token for authenticated user"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_password_hash(password):
    """get hash from password"""
    return generate_password_hash(password, "pbkdf2:sha256", salt_length=8)


@app.get("/api/v1/docs", include_in_schema=False, response_class=HTMLResponse)
async def custom_swagger_ui_html(request: Request):
    return templates.TemplateResponse(
        request,
        "custom_swagger_ui.html",
        {"title": "DUMMY-OPS API", "swagger_static_prefix": "/api/v1/static", "openapi_url": app.openapi_url}
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/api/v1/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title="DUMMY-OPS API - ReDoc",
        redoc_js_url="/api/v1/static/redoc.standalone.js",
    )


@app.post("/api/v1/token/", tags=["DEFAULT"])
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """return a jwt access token to authenticated user"""
    user = authenticate_user(str(form_data.username).lower(), form_data.password)
    if not user:
        logs_context = {"username": f"{str(form_data.username).lower()}"}
        log_events.log_event(
            "[+] FastAPI - Utilisateur inconnu cherche à obtenir un token.",
            logs_context,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom utilisateur ou mot de passe invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.post("/api/v1/register/", tags=["DEFAULT"])
async def register(user: NewUserInDBModel):
    """
    register new user.
    """
    if any(
        [
            str(user.username) == "string",
            str(user.email) == "string",
            str(user.password) == "string",
            str(user.password_check) == "string",
        ]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Saisie invalide, mot clef string non utilisable.",
        )
    valid_password = handle_passwords.check_password(str(user.password))
    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mot de passe trop simple, essayez de nouveau.",
        )
    hashed_password = generate_password_hash(
        user.password, "pbkdf2:sha256", salt_length=8
    )
    user_in_db = (
        session.query(models.User)
        .filter_by(username=str(user.username).lower())
        .first()
    )
    if user_in_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nom utilisateur existe deja, veuillez le modifier",
        )
    user_email = (
        session.query(models.User).filter_by(email=str(user.email).lower()).first()
    )
    if user_email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email existe deja en base"
        )
    if user.password != user.password_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Mots de passe ne correspondent pas",
        )

    new_user = models.User(
        username=str(user.username).lower(),
        email=str(user.email).lower(),
        hashed_password=hashed_password,
    )
    logs_context = {
        "username": f"{str(user.username).lower()}",
        "email": f"{str(user.email).lower()}",
    }
    log_events.log_event("[+] FastAPI - Création compte utilisateur.", logs_context)
    session.add(new_user)
    session.commit()
    return new_user
