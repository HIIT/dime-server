GRADLE   = ./gradlew -q
TARGET   = build/libs/dime-server-0.1.0.jar
JAVADOC_DIR = build/docs/javadoc/
JAVADOC_WEB = shell.hiit.fi:/group/reknow/public_html/javadoc/dime-server/
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
	chmod -R a+r $(JAVADOC_DIR)
	rsync -var $(JAVADOC_DIR) $(JAVADOC_WEB)
	@echo
	@echo Now open ./build/docs/javadoc/index.html
