import requests
import pandas as pd
import plotly.graph_objects as go
import concurrent.futures

DATASOURCE_IDS = [54, 56, 57, 58, 59, 73, 75, 76, 78, 120, 6, 7, 8, 9, 103, 104, 105, 106]

EXECUTOR_URL = "https://yoda-executor-1019910606111.asia-southeast1.run.app"
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


def get_chain_report(id):
    try:
        query = {
            "query": f"""
            query Reports {{
                raw_requests(
                    where: {{ data_source_id: {{ _eq: {id} }} }}
                    order_by: {{ request_id: desc }}
                    limit: 1
                ) {{
                    calldata
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
        calldata = ""
        try:
            if "errors" in result:
                return result["error"]["message"], ""
            
            raw_request = result["data"]["raw_requests"]
            if len(raw_request) == 0:
                return "No request data", ""
            
            calldata = raw_request[0]["calldata"]
            if calldata:
                calldata = bytes.fromhex(calldata[2:]).decode("utf-8", errors="ignore")

            raw_report = raw_request[0]["raw_reports"]
            if len(raw_report) == 0:
                return "No report data", ""
            
            raw_hex = raw_report[0]["data"]
            if raw_hex:
                raw_data = bytes.fromhex(raw_hex[2:]).decode("utf-8", errors="ignore")
        except (KeyError, IndexError, TypeError) as e:
            raw_data = f"Get data error {e}"

    except requests.RequestException as e:
        print(f"[ERROR] Failed for id {id}: {e}")

    return raw_data, calldata

def main():
    res = []

    def process_id(id):
        report_price, calldata = get_chain_report(id)
        executor_price = get_executor_price(id, calldata)
        return {
            "datasource id": id,
            "symbol": calldata,
            "executor price": executor_price,
            "report price": report_price
        }

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(process_id, DATASOURCE_IDS))
        res.extend(results)

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