import requests
import pandas as pd
import plotly.graph_objects as go

DATASOURCE_IDS = [54, 56, 57, 58, 59, 73, 75, 76, 78, 120, 6, 7, 8, 9, 103, 104, 105, 106]
SYMBOLS = ["BTC"]

EXECUTOR_URL = "https://us-central1-band-playground.cloudfunctions.net/yoda-executor-test"
TIMEOUT = 10000
ORACLE_BASE_URL = "https://laozi3.bandchain.org/api/oracle/v1"
CHAIN_QUERY_URL = "https://graphql-lm.bandchain.org/v1/graphql"

def get_executor_price(id, calldata):
    try:
        response = requests.get(f"{ORACLE_BASE_URL}/data_sources/{id}")
        response.raise_for_status()
        data = response.json()

        file_name = data.get("data_source", {}).get("filename")
        if not file_name:
            return "File name not found"

        executable_response = requests.get(f"{ORACLE_BASE_URL}/data/{file_name}")
        executable_response.raise_for_status()
        executable_data = executable_response.json()

        executable = executable_data.get("data")
        if not executable:
            return "Executable not found"

        payload = {
            "executable": executable,
            "calldata": calldata,
            "timeout": TIMEOUT
        }
        executor_response = requests.post(EXECUTOR_URL, json=payload)
        executor_response.raise_for_status()
        executor_response = executor_response.json()

        if executor_response.get('returncode'):
            result = executor_response.get("stderr")
        else:
            result = executor_response.get("stdout")

    except requests.RequestException as e:
        print(f"Error processing id {id}: {e}")

    return result


def get_chain_report_price(id, calldata):
    try:
        query = {
            "query": f"""
            query Reports {{
                raw_requests(
                    where: {{ data_source_id: {{ _eq: {id} }}, calldata: {{ _eq: "{calldata}" }} }}
                    order_by: {{ request_id: desc }}
                    limit: 1
                ) {{
                    raw_reports(limit: 1) {{
                        data
                    }}
                }}
            }}
            """
        }

        response = requests.post(CHAIN_QUERY_URL, json=query)
        response.raise_for_status()
        result = response.json()

        raw_data = ""
        try:
            raw_hex = result["data"]["raw_requests"][0]["raw_reports"][0]["data"]
            if raw_hex:
                raw_data = bytes.fromhex(raw_hex[2:]).decode("utf-8", errors="ignore")
        except (KeyError, IndexError, TypeError) as e:
            raw_data = f"Get data error {e}"

    except requests.RequestException as e:
        print(f"[ERROR] Failed for id {id}: {e}")

    return raw_data

def main():
    res = []

    calldata = " ".join(SYMBOLS)
    for id in DATASOURCE_IDS:
        executor_price = get_executor_price(id, calldata)
        report_price = get_chain_report_price(id, calldata)

        res.append({
            "datasource id": id,
            "symbol": calldata,
            "executor price": executor_price,
            "report price": report_price
        })

    df = pd.DataFrame(res)

    fig = go.Figure(data=[go.Table(
        header=dict(values=list(df.columns),
                    fill_color='paleturquoise',
                    align='left'),
        cells=dict(values=df.transpose().values.tolist(),
                    fill_color='lavender',
                    align='left'))
    ])

    fig.update_layout(title="Comparison Table: Executor vs Report data")
    fig.show()

if __name__ == "__main__":
    main()