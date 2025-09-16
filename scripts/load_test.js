import http from "k6/http";
import { check, sleep } from "k6";
import { Counter } from "k6/metrics";
import { b64encode } from "k6/encoding";
let ErrorCount = new Counter("errors");
const data = b64encode(open('./data_source.py'))

export default function () {
  let res = http.post("http://localhost:8000", JSON.stringify({
    "calldata": "TEST_ARG",
    "env": {
      "BAND_CHAIN_ID": "test-chain-id",
      "BAND_EXTERNAL_ID": "test-external-id",
      "BAND_REPORTER": "test-reporter",
      "BAND_REQUEST_ID": "test-request-id",
      "BAND_SIGNATURE": "test-signature",
      "BAND_VALIDATOR": "test-validator"
    },
    "executable": data,
    "timeout": 10000
  }), { headers: { 'Content-Type': 'application/json' } })

  console.log(res.body)

  let success = check(res, {
    "status is 200": (r) => r.status === 200,
  });

  if (!success) {
    ErrorCount.add(1);
  }

}
