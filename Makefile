.PHONY: lambda gcf

VERSION=2.0.4
CURRENT_DIR=$(shell pwd)

lambda:
	cp $(CURRENT_DIR)/lambda/lambda_function.py $(CURRENT_DIR)/lambda/lambda_function.bak
	RUNTIME_VERSION="lambda:$(VERSION)" envsubst < $(CURRENT_DIR)/lambda/lambda_function.bak > $(CURRENT_DIR)/lambda/lambda_function.py
	cp $(CURRENT_DIR)/requirements.txt $(CURRENT_DIR)/lambda
	docker run --rm -v $(CURRENT_DIR)/lambda:/pack python:3.9 ./pack/pack.sh
	rm $(CURRENT_DIR)/lambda/requirements.txt
	mv $(CURRENT_DIR)/lambda/lambda_function.bak $(CURRENT_DIR)/lambda/lambda_function.py

gcf:
	mv $(CURRENT_DIR)/google-cloud-functions/main.py $(CURRENT_DIR)/google-cloud-functions/main.bak
	RUNTIME_VERSION="google-cloud-function:$(VERSION)" envsubst < $(CURRENT_DIR)/google-cloud-functions/google_cloud_function.py > $(CURRENT_DIR)/google-cloud-functions/main.py
	cat requirements.txt $(CURRENT_DIR)/google-cloud-functions/extra_requirements.txt >> $(CURRENT_DIR)/google-cloud-functions/requirements.txt
	cd google-cloud-functions && zip gcf-executor.zip main.py requirements.txt && cd ..
	mv $(CURRENT_DIR)/google-cloud-functions/main.bak $(CURRENT_DIR)/google-cloud-functions/main.py
	rm $(CURRENT_DIR)/google-cloud-functions/requirements.txt

