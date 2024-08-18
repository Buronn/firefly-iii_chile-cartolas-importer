import os
import requests
import logging
import json


def get_account(token, bank):
    url = (
        os.getenv("FIREFLY_API_URL")
        + "/v1/accounts?limit=20&page=1&type=all&type=asset"
    )
    headers = {"accept": "application/vnd.api+json", "Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)

    try:
        response.raise_for_status()  # Levanta un error si el código de estado HTTP es 4xx/5xx
        # Verificar si la respuesta tiene contenido antes de intentar decodificarla
        if response.text:
            logging.info(f"Response content: {response.text}")
            data = response.json()
            account_id = next(
                (
                    account["id"]
                    for account in data["data"]
                    if bank.lower() in account["attributes"]["name"].lower()
                ),
                None,
            )

            logging.info(f"Account ID: {account_id}")
            if account_id:
                return account_id
            raise ValueError(f"Account not found for bank: {bank}")
        else:
            logging.warning("Response is empty.")
            return None
    except requests.exceptions.HTTPError as http_err:
        logging.error(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error occurred: {req_err}")
    return None


def create_import_load(token, bank, file_path, session_id):

    import_url = (
        os.getenv("AUTO_IMPORT_URL")
        + "/autoupload?secret="
        + os.getenv("AUTO_IMPORT_SECRET")
    )
    account_id = get_account(token, bank)
    # Leer la configuración del banco desde el JSON
    config_path = f"/app/configs/{bank}.json"
    with open(config_path, "r") as f:
        config_data = json.load(f)

    # Modificar la variable "default_account"
    config_data["default_account"] = int(account_id)

    # Guardar el JSON modificado en un nuevo archivo temporal
    modified_config_path = f"/app/configs/{bank}_{session_id}.json"
    with open(modified_config_path, "w") as f:
        json.dump(config_data, f)

    # Configurar los headers
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}

    # Realizar la solicitud POST para la importación
    response = requests.post(
        import_url,
        headers=headers,
        files={
            "importable": open(file_path, "rb"),
            "json": open(modified_config_path, "rb"),
        },
    )

    # Verificar la respuesta
    if response.status_code == 200:
        logging.info("Import successful!")
        # Eliminar el archivo temporal
        os.remove(modified_config_path)
    else:
        logging.error(f"Import failed with status code {response.status_code}")
        logging.error(response.text)
        # Eliminar el archivo temporal
        os.remove(modified_config_path)
