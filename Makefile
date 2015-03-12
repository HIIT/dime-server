GRADLE    = ./gradlew -q
TARGET   = build/libs/dime-server-0.1.0.jar
SOURCES := $(shell find src/ -name '[A-Z]*.java' -or -name '*.html')

all:	build

build:  $(TARGET)

$(TARGET): $(SOURCES)
	$(GRADLE) build

run:    $(TARGET)
	java -jar $(TARGET)

clean:
	$(GRADLE) clean

doc: $(SOURCES)
	$(GRADLE) javadoc
	@echo
	@echo Now open ./build/docs/javadoc/index.html
