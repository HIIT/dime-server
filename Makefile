GRADLE   = ./gradlew -q
TARGET   = build/libs/dime-server-0.1.0.jar
JAVADOC_DIR = build/docs/javadoc/
JAVADOC_WEB = shell.hiit.fi:/group/reknow/public_html/javadoc/dime-server/
SOURCES := $(shell find src/ -name '[A-Z]*.java' -or -name '*.html')

DOCKER_DB_DIR = ~/dime-db

all:	assemble

assemble:  $(TARGET)

$(TARGET): $(SOURCES)
	$(GRADLE) assemble

run:    $(TARGET)
	java -jar $(TARGET)

test:
	$(GRADLE) test
	@echo Now open ./build/reports/tests/index.html

clean:
	$(GRADLE) clean

doc: $(SOURCES)
	$(GRADLE) javadoc
	chmod -R a+r $(JAVADOC_DIR)
	rsync -var $(JAVADOC_DIR) $(JAVADOC_WEB)
	@echo
	@echo Now open ./build/docs/javadoc/index.html

docker: $(TARGET)
	docker build -t dime-server .

docker_db_dir:
	@echo Creating directory for mongodb ...
	mkdir $(DOCKER_DB_DIR)
	chmod 777 $(DOCKER_DB_DIR)

runDocker: docker docker_db_dir
	docker run -it -p 8080:8080 -v $(DOCKER_DB_DIR):/var/lib/mongodb dime-server
