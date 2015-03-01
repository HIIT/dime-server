package dime;

import java.util.concurrent.atomic.AtomicLong;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.beans.factory.annotation.Autowired;

@RestController
public class DiMeController {

    private static final String template = "Hello, %s!";
    private final AtomicLong counter = new AtomicLong();

    private final AppEventRepository appEventRepository;

    @Autowired
    DiMeController(AppEventRepository appEventRepository) {
	this.appEventRepository = appEventRepository;
    }

    @RequestMapping("/logger")
    public AppEvent logger(@RequestBody AppEvent input) {
	AppEvent appEvent = appEventRepository.save(input);
	return appEvent;
    }
}
