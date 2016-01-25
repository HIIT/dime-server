if defined JAVA_HOME goto useJavaHome

set JAVA_EXE=java.exe

%JAVA_EXE% -version >NUL 2>&1
if "%ERRORLEVEL%" == "0" goto runIt

:useJavaHome
set JAVA_HOME=%JAVA_HOME:"=%
set JAVA_EXE=%JAVA_HOME%/bin/java.exe

:runIt
"%JAVA_EXE%" -jar dime-server.jar
