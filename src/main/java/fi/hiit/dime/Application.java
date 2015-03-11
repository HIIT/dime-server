package fi.hiit.dime;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.servlet.mvc.method.annotation.AbstractJsonpResponseBodyAdvice;
import org.springframework.web.bind.annotation.ControllerAdvice;

@SpringBootApplication
public class Application {

    @ControllerAdvice
    static class JsonpAdvice extends AbstractJsonpResponseBodyAdvice {
	public JsonpAdvice() {
	    super("callback");
	}
    }

    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
