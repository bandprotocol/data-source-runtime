from fastapi import FastAPI, Request, HTTPException
import shutil
import os
import shlex
import subprocess
import base64

# Set environment flag of MAX_EXECUTABLE, MAX_DATA_SIZE

runtime_version = "docker-executor:0.2.4"
app = FastAPI()

def get_env(env, flag):
    if flag not in env:
        raise Exception(flag + " is missing")
    return int(env[flag])

@app.post("/")
async def execute(request: Request):
    env = os.environ.copy()

    MAX_EXECUTABLE = get_env(env, "MAX_EXECUTABLE")
    MAX_DATA_SIZE = get_env(env, "MAX_DATA_SIZE")

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
    if "timeout" not in request_json:
        raise HTTPException(status_code=400, detail="Missing timeout value")
    try:
        timeout = int(request_json["timeout"])
    except ValueError:
        raise HTTPException(status_code=400, detail="Timeout format invalid")

    user_folder = request_json["env"]["BAND_REQUEST_ID"]+"-"+request_json["env"]["BAND_EXTERNAL_ID"]
    os.mkdir(user_folder)
    path = user_folder+"/execute.sh"
    with open(path, "w+") as f:
        f.write(executable.decode())

    os.chmod(path, 0o777)
    try:
        env = os.environ.copy()
        for key, value in request_json.get("env", {}).items():
            env[key] = value
        os.environ.update(env)
        # proc = subprocess.Popen(
        #     [path] + shlex.split(request_json["calldata"]),
        #     env=env,
        #     stdout=subprocess.PIPE,
        #     stderr=subprocess.PIPE,
        # )

        # proc.wait(timeout=(timeout / 1000))
        # returncode = proc.returncode
        # stdout = proc.stdout.read(MAX_DATA_SIZE).decode()
        # stderr = proc.stderr.read(MAX_DATA_SIZE).decode()
        returnCode = os.system(path +" "+ ' '.join(shlex.split(request_json["calldata"])) + " > output.txt 2> error.txt")
        output = open("output.txt").read(MAX_DATA_SIZE)
        error = open("error.txt").read(MAX_DATA_SIZE)
        shutil.rmtree(user_folder)
        return {
                "returncode": returnCode,
                "stdout": output,
                "stderr": error,
                "err": "",
                "version": runtime_version,
            }
    except OSError:
        shutil.rmtree(user_folder)
        return {
                "returncode": 126,
                "stdout": "",
                "stderr": "",
                "err": "Execution fail",
                "version": runtime_version,
            }
    except subprocess.TimeoutExpired:
        shutil.rmtree(user_folder)
        return {
                "returncode": 111,
                "stdout": "",
                "stderr": "",
                "err": "Execution time limit exceeded",
                "version": runtime_version,
            }
