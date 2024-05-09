"""
All the tests functions to checkt users passwords against the policy.
Notice that by default we already add dummies data through the application utils module.
"""


from app.packages import handle_passwords


def test_check_password():
    """
    Description: check if user password enough complex.
    """
    user_passwords_list = [
        ("applepie", False),
        ("applepie94", False),
        ("applepie,94", False),
        ("@pplepie94", True),
    ]
    for password in user_passwords_list:
        response = handle_passwords.check_password(password[0])
        assert response is password[1]
