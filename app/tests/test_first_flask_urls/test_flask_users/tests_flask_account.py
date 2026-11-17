"""
All the tests functions for the self-service account urls:
- delete own account (validated through an emailed confirmation link)
- update own email (validated through a link emailed to the new address)
Notice that by default we already add dummies data through the application utils module.
"""

import html

import pytest

import app.packages.flask_app.project as project
from app.packages.database.commands import session_commands
from app.packages.database.models.models import User


@pytest.fixture
def capture_sent_emails(monkeypatch):
    """
    Description: replace project._send_email by a fake which records the emails.
    In SCOPE=test _send_email is a no-op, so we patch it to assert on sent mails.
    """
    sent = []

    def fake_send_email(to_email, subject, html_content):
        sent.append({"to": to_email, "subject": subject, "html": html_content})

    monkeypatch.setattr(project, "_send_email", fake_send_email)
    return sent


@pytest.fixture
def failing_send_email(monkeypatch):
    """
    Description: replace project._send_email by a fake which always fails.
    """

    def boom(to_email, subject, html_content):
        raise Exception("SMTP unreachable")

    monkeypatch.setattr(project, "_send_email", boom)


def make_deletion_token(user_id, email):
    """
    Description: build a valid account deletion token, as the one emailed to the user.
    """
    return project.sengrid_tokens_serializer.dumps(
        {"user_id": user_id, "email": email},
        salt=project.ACCOUNT_DELETION_TOKEN_SALT,
    )


def make_email_change_token(user_id, new_email):
    """
    Description: build a valid email change token, as the one emailed to the new address.
    """
    return project.sengrid_tokens_serializer.dumps(
        {"user_id": user_id, "new_email": new_email},
        salt=project.EMAIL_CHANGE_TOKEN_SALT,
    )


def create_throwaway_user(get_session, username, email):
    """
    Description: create a disposable user so that deletion/update tests do not
    alter the shared dummy users (admin id 1, donald id 2, daisy id 3, ...).
    Any leftover user with the same username or email is removed first, so the
    helper is safe to re-run even if a previous test failed before its cleanup.
    Returns the new user id.
    """
    old = get_session.query(User).filter_by(username=username).first()
    if old:
        get_session.delete(old)
        get_session.commit()
    old_email = get_session.query(User).filter_by(email=email).first()
    if old_email:
        get_session.delete(old_email)
        get_session.commit()
    user = User(
        username=username,
        email=email,
        hashed_password="dummy",
        is_active=True,
        disabled=False,
    )
    get_session.add(user)
    get_session.commit()
    return user.id


def get_user_id(username):
    """
    Description: return the id of a user, or None if he does not exist.
    Uses a scalar query so the result stays valid after the session is closed.
    """
    session = session_commands.get_a_database_session()
    user_id = session.query(User.id).filter_by(username=username).scalar()
    session.close()
    return user_id


def get_user_email(username):
    """
    Description: return the email of a user as a plain string
    (safe to use after the session is closed, no DetachedInstanceError).
    """
    session = session_commands.get_a_database_session()
    email = session.query(User.email).filter_by(username=username).scalar()
    session.close()
    return email


def cleanup_user(username):
    """
    Description: remove a throwaway user at the end of a test.
    """
    session = session_commands.get_a_database_session()
    user = session.query(User).filter_by(username=username).first()
    if user:
        session.delete(user)
        session.commit()
    session.close()


# ------------------------------------------------------------------
# /account/delete/ : demande de suppression de son propre compte
# ------------------------------------------------------------------

def test_flask_get_delete_account_without_authentication(client):
    """
    Description: the delete account page requires authentication.
    """
    response = client.get("/account/delete/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_get_delete_account_page(client, access_session, captured_templates):
    """
    Description: GET on the delete account page re-renders the confirmation form.
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get("/account/delete/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"SUPPRIMER MON COMPTE" in response.data
    assert captured_templates[0].name == "delete_account.html"


def test_flask_get_delete_account_page_as_admin_is_refused(client, access_session_as_admin):
    """
    Description: the admin account (id 1) cannot be deleted, even by the admin himself.
    """
    headers = {"Cookie": f"session={access_session_as_admin}"}
    response = client.get("/account/delete/", headers=headers, follow_redirects=True)
    assert response.status_code == 403


def test_flask_post_delete_account_sends_confirmation_email(
    client, access_session, get_flask_csrf_token, capture_sent_emails, captured_templates
):
    """
    Description: POST on the delete account page emails a signed confirmation link
    to the current email. The account is NOT deleted yet.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "/account/delete/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert captured_templates[0].name == "account_deletion_link_sent.html"
    assert len(capture_sent_emails) == 1
    assert capture_sent_emails[0]["to"] == "donald@localhost.fr"
    assert "/account/delete/confirm/" in capture_sent_emails[0]["html"]
    assert get_user_id("donald") is not None


def test_flask_post_delete_account_when_email_sending_fails(
    client, access_session, get_flask_csrf_token, failing_send_email, captured_templates
):
    """
    Description: if the confirmation email cannot be sent, the mail_not_sent page
    is rendered and the account is kept.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {"csrf_token": get_flask_csrf_token}
    response = client.post(
        "/account/delete/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert captured_templates[0].name == "mail_not_sent.html"
    assert get_user_id("donald") is not None


# ------------------------------------------------------------------
# /account/delete/confirm/<token> : validation du lien reçu par mail
# ------------------------------------------------------------------

def test_flask_confirm_account_deletion_with_invalid_token(client):
    """
    Description: an invalid/expired token redirects with an error flash.
    """
    response = client.get("/account/delete/confirm/123oclock", follow_redirects=True)
    assert response.status_code == 200
    assert "Le lien de confirmation n'est pas valide ou a expiré." in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_confirm_account_deletion_with_unknown_user(client):
    """
    Description: a valid token pointing to an unknown user is refused.
    """
    token = make_deletion_token(55555555, "nobody@localhost.fr")
    response = client.get(f"/account/delete/confirm/{token}", follow_redirects=True)
    assert response.status_code == 200
    assert "Le lien de confirmation n'est pas valide ou a expiré." in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_confirm_account_deletion_with_email_mismatch(client, get_session):
    """
    Description: a token whose email does not match the account current email
    is refused (guards against an email change since the link was sent).
    """
    user_id = create_throwaway_user(get_session)
    token = make_deletion_token(user_id, "another@localhost.fr")
    response = client.get(f"/account/delete/confirm/{token}", follow_redirects=True)
    assert response.status_code == 200
    assert "Le lien de confirmation n'est pas valide ou a expiré." in html.unescape(
        response.get_data(as_text=True)
    )
    assert get_user_by_username("accounttest") is not None
    cleanup_user("accounttest")


def test_flask_confirm_account_deletion_of_admin_is_refused(client):
    """
    Description: the admin account cannot be deleted through the emailed link.
    """
    token = make_deletion_token(1, "admin@localhost.fr")
    response = client.get(f"/account/delete/confirm/{token}", follow_redirects=True)
    assert response.status_code == 403
    assert get_user_id("admin") is not None


def test_flask_confirm_account_deletion_with_valid_token(client, get_session):
    """
    Description: a valid token deletes the account.
    """
    user_id = create_throwaway_user(get_session)
    token = make_deletion_token(user_id, "accounttest@localhost.fr")
    response = client.get(f"/account/delete/confirm/{token}", follow_redirects=True)
    assert response.status_code == 200
    assert "supprimé" in html.unescape(response.get_data(as_text=True))
    assert get_user_id("accounttest") is None


# ------------------------------------------------------------------
# /account/email/ : demande de changement de son propre email
# ------------------------------------------------------------------

def test_flask_get_update_email_without_authentication(client):
    """
    Description: the update email page requires authentication.
    """
    response = client.get("/account/email/", follow_redirects=False)
    assert response.status_code == 302


def test_flask_get_update_email_page(client, access_session, captured_templates):
    """
    Description: GET on the update email page re-renders the form.
    """
    headers = {"Cookie": f"session={access_session}"}
    response = client.get("/account/email/", headers=headers, follow_redirects=True)
    assert response.status_code == 200
    assert b"MISE A JOUR EMAIL" in response.data
    assert captured_templates[0].name == "update_email.html"


def test_flask_post_update_email_sends_confirmation_to_new_address(
    client, access_session, get_flask_csrf_token, capture_sent_emails, captured_templates
):
    """
    Description: POST on the update email page emails a signed confirmation link
    to the NEW email address (proof of ownership). The email is NOT updated yet.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {
        "new_email": "donald2@localhost.fr",
        "new_email_check": "donald2@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/account/email/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert captured_templates[0].name == "email_change_link_sent.html"
    assert len(capture_sent_emails) == 1
    assert capture_sent_emails[0]["to"] == "donald2@localhost.fr"
    assert "/account/email/confirm/" in capture_sent_emails[0]["html"]
    assert get_user_email("donald") == "donald@localhost.fr"


def test_flask_post_update_email_with_mismatched_emails(
    client, access_session, get_flask_csrf_token
):
    """
    Description: new email and its confirmation must match.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {
        "new_email": "donald2@localhost.fr",
        "new_email_check": "donald3@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/account/email/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Les emails ne correspondent pas." in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_post_update_email_with_same_email(
    client, access_session, get_flask_csrf_token
):
    """
    Description: the new email must differ from the current one.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {
        "new_email": "donald@localhost.fr",
        "new_email_check": "donald@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/account/email/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Le nouvel email est identique à l'actuel." in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_post_update_email_with_existing_email(
    client, access_session, get_flask_csrf_token
):
    """
    Description: the new email must not be already used (daisy's email here).
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {
        "new_email": "daisy@localhost.fr",
        "new_email_check": "daisy@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/account/email/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert "Email existe deja en base" in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_post_update_email_when_email_sending_fails(
    client, access_session, get_flask_csrf_token, failing_send_email, captured_templates
):
    """
    Description: if the confirmation email cannot be sent, the mail_not_sent page
    is rendered and the email is kept unchanged.
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Cookie": f"session={access_session}",
    }
    data = {
        "new_email": "donald2@localhost.fr",
        "new_email_check": "donald2@localhost.fr",
        "csrf_token": get_flask_csrf_token,
    }
    response = client.post(
        "/account/email/", headers=headers, data=data, follow_redirects=True
    )
    assert response.status_code == 200
    assert captured_templates[0].name == "mail_not_sent.html"
    assert get_user_email("donald") == "donald@localhost.fr"


# ------------------------------------------------------------------
# /account/email/confirm/<token> : validation du lien reçu sur la nouvelle adresse
# ------------------------------------------------------------------

def test_flask_confirm_email_change_with_invalid_token(client):
    """
    Description: an invalid/expired token redirects with an error flash.
    """
    response = client.get("/account/email/confirm/123oclock", follow_redirects=True)
    assert response.status_code == 200
    assert "Le lien de confirmation n'est pas valide ou a expiré." in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_confirm_email_change_with_unknown_user(client):
    """
    Description: a valid token pointing to an unknown user is refused.
    """
    token = make_email_change_token(55555555, "new@localhost.fr")
    response = client.get(f"/account/email/confirm/{token}", follow_redirects=True)
    assert response.status_code == 200
    assert "Le lien de confirmation n'est pas valide ou a expiré." in html.unescape(
        response.get_data(as_text=True)
    )


def test_flask_confirm_email_change_with_valid_token(client, get_session):
    """
    Description: a valid token updates the user's email in database.
    """
    user_id = create_throwaway_user(get_session)
    token = make_email_change_token(user_id, "accounttest_new@localhost.fr")
    response = client.get(f"/account/email/confirm/{token}", follow_redirects=True)
    assert response.status_code == 200
    assert "Email mis à jour" in html.unescape(response.get_data(as_text=True))
    assert get_user_by_username("accounttest").email == "accounttest_new@localhost.fr"
    cleanup_user("accounttest")


def test_flask_confirm_email_change_with_email_taken_by_another_user(
    client, get_session
):
    """
    Description: if the new email has been taken by another account since the link
    was sent, the validation is refused and the email is kept unchanged.
    """
    user_id = create_throwaway_user(get_session)
    token = make_email_change_token(user_id, "donald@localhost.fr")
    response = client.get(f"/account/email/confirm/{token}", follow_redirects=True)
    assert response.status_code == 200
    assert "Cet email est deja utilisé par un autre compte." in html.unescape(
        response.get_data(as_text=True)
    )
    assert get_user_by_username("accounttest").email == "accounttest@localhost.fr"
    cleanup_user("accounttest")


def test_flask_confirm_account_deletion_with_email_mismatch(client, get_session):
    """
    Description: a token whose email does not match the account current email
    is refused (guards against an email change since the link was sent).
    """
    user_id = create_throwaway_user(
        get_session,
        username="accounttest_del_mismatch",
        email="accounttest_del_mismatch@localhost.fr",
    )
    try:
        token = make_deletion_token(user_id, "another@localhost.fr")
        response = client.get(
            f"/account/delete/confirm/{token}", follow_redirects=True
        )
        assert response.status_code == 200
        assert "Le lien de confirmation n'est pas valide ou a expiré." in html.unescape(
            response.get_data(as_text=True)
        )
        assert get_user_id("accounttest_del_mismatch") is not None
    finally:
        cleanup_user("accounttest_del_mismatch")


def test_flask_confirm_account_deletion_with_valid_token(client, get_session):
    """
    Description: a valid token deletes the account.
    """
    user_id = create_throwaway_user(
        get_session,
        username="accounttest_del",
        email="accounttest_del@localhost.fr",
    )
    try:
        token = make_deletion_token(user_id, "accounttest_del@localhost.fr")
        response = client.get(
            f"/account/delete/confirm/{token}", follow_redirects=True
        )
        assert response.status_code == 200
        assert "supprimé" in html.unescape(response.get_data(as_text=True))
        assert get_user_id("accounttest_del") is None
    finally:
        cleanup_user("accounttest_del")  # no-op si la suppression a réussi


def test_flask_confirm_email_change_with_valid_token(client, get_session):
    """
    Description: a valid token updates the user's email in database.
    """
    user_id = create_throwaway_user(
        get_session,
        username="accounttest_mail",
        email="accounttest_mail@localhost.fr",
    )
    try:
        token = make_email_change_token(user_id, "accounttest_mail_new@localhost.fr")
        response = client.get(
            f"/account/email/confirm/{token}", follow_redirects=True
        )
        assert response.status_code == 200
        assert "Email mis à jour" in html.unescape(response.get_data(as_text=True))
        assert get_user_email("accounttest_mail") == "accounttest_mail_new@localhost.fr"
    finally:
        cleanup_user("accounttest_mail")


def test_flask_confirm_email_change_with_email_taken_by_another_user(
    client, get_session
):
    """
    Description: if the new email has been taken by another account since the link
    was sent, the validation is refused and the email is kept unchanged.
    """
    user_id = create_throwaway_user(
        get_session,
        username="accounttest_taken",
        email="accounttest_taken@localhost.fr",
    )
    try:
        token = make_email_change_token(user_id, "donald@localhost.fr")
        response = client.get(
            f"/account/email/confirm/{token}", follow_redirects=True
        )
        assert response.status_code == 200
        assert "Cet email est deja utilisé par un autre compte." in html.unescape(
            response.get_data(as_text=True)
        )
        assert get_user_email("accounttest_taken") == "accounttest_taken@localhost.fr"
    finally:
        cleanup_user("accounttest_taken")