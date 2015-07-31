GRADLE   = ./gradlew -q
TARGET   = build/libs/dime-server-0.1.0.jar
APIDOC   = apidoc
APIDOC_WEB = shell.hiit.fi:/group/reknow/public_html/apidoc/dime-server/
SOURCES := $(shell find src/ -name '[A-Z]*.java' -or -name '*.html')

all:	build

build:  $(TARGET)

$(TARGET): $(SOURCES)
	$(GRADLE) build

run:    $(TARGET)
	java -jar $(TARGET)

test:
	$(GRADLE) test
	@echo Now open ./build/reports/tests/index.html

clean:
	$(GRADLE) clean

doc: $(SOURCES)
	$(GRADLE) javadoc
	@echo
	@echo Now open ./build/docs/javadoc/index.html

apidoc: $(SOURCES)
	$(APIDOC) -i src/main -o build/apidoc/
	rsync -vr build/apidoc/ $(APIDOC_WEB)
	@echo Now open ./build/apidoc/index.html
