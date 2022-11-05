LAMBDA_NAME=B-L475E-IOT01A2-Handler
RELEASE_PATH=releases/lambda_function_v1.zip
CERTS_PATH=certs
PACKAGE_PATH=package
USER_CONFIGS=user_configs.sh

all: clean AWSIoTPythonSDK ask-sdk-core zip-package zip-lambda-function
	@ echo ''
	@ echo ''
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
	zip -r9 $(RELEASE_PATH) $(PACKAGE_PATH)

zip-lambda-function:
	@ echo ''
	@ echo ''
	@ echo '-> Ziping lambda_function:'
	zip -g $(RELEASE_PATH) lambda_function.py

zip-certs:
	@ echo ''
	@ echo ''
	@ echo '-> Ziping certs:'
	zip -g $(RELEASE_PATH) $(CERTS_PATH)/*

clean:
	rm -rf package $(RELEASE_PATH)

setup:
	@ echo '-> Running setup script:'
	sh ./$(USER_CONFIGS)

deploy: setup
	@ echo '-> B-L475E-IOT01A2-Handler deploy:'
	aws lambda update-function-code --function-name ${LAMBDA_NAME} --zip-file fileb://$(RELEASE_PATH)
