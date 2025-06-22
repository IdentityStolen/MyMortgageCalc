import requests
import json
from .settings_local import NINJA_API_KEY


# ToDO
def get_data(loan, interest_rate, term):
    try:
        api_url = f"https://api.api-ninjas.com/v1/mortgagecalculator?loan_amount={loan}&interest_rate={interest_rate}&duration_years={term}"
        response = requests.get(api_url, headers={"X-Api-Key": f"{NINJA_API_KEY}"})
        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            return data["monthly_payment"]["total"], data["total_interest_paid"]
        else:
            response.raise_for_status()
    except Exception as e:
        raise e
