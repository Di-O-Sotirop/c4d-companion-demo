ROOT 		:= $(patsubst %/,%, $(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

APP_NAME	?= aes_sw

SRC_DIR			:= $(ROOT)/src
INC_DIR			:= $(SRC_DIR)/inc
BUILD_DIR		:= $(ROOT)/build

.PHONY: build clean

all: env build

deploy: clean_board
	@echo -e "Deploying '$(APP_NAME)' to '$(HERO_TARGET_HOST):$(HERO_TARGET_PATH_APPS)/$(APP_NAME)'"
	@scp $(BUILD_DIR)/$(APP_NAME) $(HERO_TARGET_HOST):$(HERO_TARGET_PATH_APPS)

build: 
	@echo -e "Building application '$(APP_NAME)'"
	@cd build && make -s clean all

env:
	@mkdir -p build && cd build && cmake ./.. \
		-DCMAKE_APP_ROOT:PATH=$(ROOT) \
		-DCMAKE_APP_INC:PATH=$(ROOT)/src/inc

clean:
	@rm -rf build

clean_board:
	@echo -e "Cleaning '$(HERO_TARGET_HOST):$(HERO_TARGET_PATH_APPS)/$(APP_NAME)'"
	@ssh $(HERO_TARGET_HOST) "rm -f $(HERO_TARGET_PATH_APPS)/$(APP_NAME)"
