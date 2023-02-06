from fastapi import FastAPI, Request, HTTPException
import os
import shlex
import base64
import sys
import io

# preload
import preload

runtime_version = "docker-executor:0.2.4"
app = FastAPI()


def get_env(env, flag):
    if flag not in env:
        raise Exception(flag + " is missing")
    return int(env[flag])


@app.post("/")
async def execute(request: Request):
    base_env = os.environ.copy()

    MAX_EXECUTABLE = get_env(base_env, "MAX_EXECUTABLE")
    MAX_DATA_SIZE = get_env(base_env, "MAX_DATA_SIZE")

    request_json = await request.json()

    if "executable" not in request_json:
        raise HTTPException(status_code=400, detail="Missing executable value")
    executable = base64.b64decode(request_json["executable"])
    if len(executable) > MAX_EXECUTABLE:
        raise HTTPException(status_code=400, detail="Executable exceeds max size")
    if "calldata" not in request_json:
        raise HTTPException(status_code=400, detail="Missing calldata value")
    if len(request_json["calldata"]) > MAX_DATA_SIZE:
        raise HTTPException(status_code=400, detail="Calldata exceeds max size")

    res = {
        "returncode": 0,
        "stdout": "",
        "stderr": "",
        "err": "",
        "version": runtime_version,
    }

    out = io.StringIO()
    err = io.StringIO()

    try:
        sys.stdout = out
        sys.stderr = err
        sys.argv = shlex.split("file " + request_json["calldata"])

        env = os.environ.copy()
        for key, value in request_json.get("env", {}).items():
            env[key] = value
        os.environ.update(env)

        exec(executable.decode(), {"__name__": "__main__"})
    except BaseException as e:
        res["returncode"] = 126
        res["err"] = "Execution fail"
    finally:
        os.environ.update(base_env)
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        res["stdout"] = out.getvalue()[:MAX_DATA_SIZE]
        res["stderr"] = err.getvalue()[:MAX_DATA_SIZE]

        if len(res["stderr"]) != 0:
            res["returncode"] = 1

        return res
