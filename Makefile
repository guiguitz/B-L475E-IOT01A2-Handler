LAMBDA_NAME=B-L475E-IOT01A2-Handler
RELEASE_PATH=releases/lambda_function_v0.zip
PACKAGE_PATH=package
CERTS_PATH=certs
USER_CONFIGS=user_configs.sh

all: clean AWSIoTPythonSDK ask-sdk-core zip-package zip-lambda-function zip-certs deploy
	@ echo ''
	@ echo ''
	rm -rf package
	@ echo 'Finished!'

AWSIoTPythonSDK:
	@ echo ''
	@ echo ''
	@ echo '-> Installing AWSIoTPythonSDK package:'
	pip install --target $(PACKAGE_PATH) AWSIoTPythonSDK

ask-sdk-core:
	@ echo ''
	@ echo ''
	@ echo '-> Installing ask-sdk-core package:'
	pip install --target $(PACKAGE_PATH) ask-sdk-core

zip-package:
	@ echo ''
	@ echo ''
	@ echo '-> Ziping dependencies:'
	cd $(PACKAGE_PATH) && zip -r9 -u ../$(RELEASE_PATH) . -q

zip-lambda-function:
	@ echo ''
	@ echo ''
	@ echo '-> Ziping lambda_function:'
	zip -g $(RELEASE_PATH) lambda_function.py

zip-certs:
	@ echo ''
	@ echo ''
	@ echo '-> Ziping certs:'
	zip -g $(RELEASE_PATH) $(wildcard $(CERTS_PATH)/*)

clean:
	rm -rf package $(RELEASE_PATH)

setup:
	@ echo '-> Running setup script:'
	sh ./$(USER_CONFIGS)

deploy:
	@ echo '-> B-L475E-IOT01A2-Handler deploy:'
	aws lambda update-function-code --function-name ${LAMBDA_NAME} --zip-file fileb://$(RELEASE_PATH)
