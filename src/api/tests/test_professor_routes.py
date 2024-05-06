from core.application import client

from core.base_professor import (
    alternative_email,
    alternative_name,
    alternative_role,
    email, 
    name, 
    password,
    role,
    user_id
)


valid_form = {
    "nome": name,
    "email": email,
    "role": role,
    "senha": password,
}


def test_create_professor():
    """
    Test route for creating a new professor.
    """
    url = "/professores/"

    # Test sending a form with bad information.
    invalid_form_cases = [
        {"nome": ""},                                                                          # Empty name
        {"nome": " " * 20},                                                                    # Blank name
        {"nome": "N"},                                                                         # Short name
        {"nome": "Je4n L0u1"},                                                                 # Illegal name
        {"email": ""},                                                                         # Empty email
        {"email": " " * 20},                                                                   # Blank email
        {"email": email.replace("@", "")},                                                     # Invalid email (no domain)
        {"email": email.split("@")[0] + "@"},                                                  # Invalid email (no domain name)
        {"email": email.split("@")[0] + "some@name@ufba.br"},                                  # Invalid email (illegal char)
        {"role": ""},                                                                          # Empty role
        {"role": " " * 20},                                                                    # Blank role
        {"role": "SomeRole"},                                                                  # Illegal role
        {"senha": ""},                                                                         # Empty password
        {"senha": " " * 10},                                                                   # Blank password
        {"senha": password + " " + "something"},                                               # Illegal password (with spaces)
        {"senha": password[:3]},                                                               # Short password
    ]
    for invalid_form in invalid_form_cases:
        form = valid_form.copy()
        form.update(invalid_form)

        assert client.post(url, json=form).status_code >= 400

    # Test sending a incomplete form.
    for key in valid_form.keys():
        form = valid_form.copy()
        form.pop(key)

        assert client.post(url, json=form).status_code >= 400

    # Test sending a valid form.
    assert 200 <= client.post(url, json=valid_form).status_code <= 299

    # Test sending the same valid form again (you should NOT be able to create the same professor again).
    assert client.post(url, json=valid_form).status_code >= 400

    # Test sending a different form but with an email that already exists on database.
    form = valid_form.copy()
    form["nome"] = "Another Guy"
    form["senha"] = "AnotherPassword"
    assert client.post(url, json=form).status_code >= 400

    # Test sending a form with the same data, except the identication.
    form = valid_form.copy()
    form["email"] = alternative_email
    assert 200 <= client.post(url, json=form).status_code <= 299


def test_get_professor():
    """
    Test route for getting the professor from the database.
    """
    expected = {"nome": name, "email": email, "role": role}
    
    response = client.get(f"/professores/{user_id}")
    assert 200 <= response.status_code <= 299

    result = response.json()

    for key, value in expected.items():
        assert result.get(key, "") == value


def test_get_professor_by_email():
    """
    Test route for getting the professor from the database by his email.
    """
    expected = {"nome": name, "email": email, "role": role}
    
    response = client.get(f"/professores/email/{email}")
    assert 200 <= response.status_code <= 299

    result = response.json()

    for key, value in expected.items():
        assert result.get(key, "") == value


def test_update_professor():
    """
    Test route for updating the professor's information on the database.
    """
    url = f"/professores/{user_id}"

    new_data = {"nome": alternative_name, "email": alternative_email.split("@")[0] + "foo" + "@ufmg.br", "role": alternative_role}
    
    # Update user's information.
    form = valid_form.copy()
    form.update(new_data)
    form.pop("senha")

    response = client.put(url, json=form)
    assert 200 <= response.status_code <= 299

    # Get the user's information and check the changes.
    response = client.get(url)
    assert 200 <= response.status_code <= 299

    result = response.json()

    for key, value in new_data.items():
        assert result.get(key, "") == value
    

def test_delete_professor():
    """
    Test route for deleting the professor from the database.
    """
    url = f"/professores/{user_id}"

    # Try to get the user.
    response = client.get(url)
    assert 200 <= response.status_code <= 299

    # Update user's information.
    response = client.delete(url)
    assert 200 <= response.status_code <= 299

    # Try to get the deleted user.
    response = client.get(url)
    assert response.status_code >= 400